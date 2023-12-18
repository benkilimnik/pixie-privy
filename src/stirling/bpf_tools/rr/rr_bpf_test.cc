/*
 * Copyright 2018- The Pixie Authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <sys/syscall.h>

#include <gtest/gtest.h>

#include <memory>
#include <set>
#include <vector>

#include "src/common/testing/testing.h"
#include "src/stirling/bpf_tools/bcc_wrapper.h"
#include "src/stirling/bpf_tools/macros.h"
#include "src/stirling/bpf_tools/rr/rr.h"
#include "src/stirling/obj_tools/address_converter.h"
#include "src/stirling/utils/proc_path_tools.h"

using px::stirling::obj_tools::ElfAddressConverter;
using px::stirling::obj_tools::ElfReader;

DEFINE_uint32(other_program_pid, 0, "Other program pid.");

// Create a std::string_view named rr_test_bcc_script based on the bazel target :rr_test_bpf_text.
// This is the BPF program we will invoke for this test.
OBJ_STRVIEW(rr_test_bcc_script, rr_test_bpf_text);

namespace test {

// We attach an eBPF user space probe to Foo() and Bar(). Later, we invoke Foo() and Bar()
// and expect that the eBPF recording mechanism records the perf buffer traffic generated
// by our eBPF probe.
NO_OPT_ATTR uint32_t Foo(const uint32_t arg) { return 1 + arg; }

std::vector<int> gold_data;
uint32_t test_idx = 0;

void PerfBufferRecordingDataFn(void* cb_cookie, void* data, int data_size) {
  DCHECK(cb_cookie != nullptr) << "Perf buffer callback not set-up properly. Missing cb_cookie.";
  EXPECT_EQ(data_size, sizeof(int));
  int v = *static_cast<int*>(data);
  gold_data.push_back(v);
}

void PerfBufferReplayingDataFn(void* cb_cookie, void* data, int data_size) {
  DCHECK(cb_cookie != nullptr) << "Perf buffer callback not set-up properly. Missing cb_cookie.";
  EXPECT_EQ(data_size, sizeof(int));
  int v = *static_cast<int*>(data);
  EXPECT_EQ(gold_data[test_idx], v);
  ++test_idx;
}

void PerfBufferLossFn(void* cb_cookie, uint64_t /*lost*/) {
  DCHECK(cb_cookie != nullptr) << "Perf buffer callback not set-up properly. Missing cb_cookie.";
}

}  // namespace test

namespace px {
namespace stirling {

using bpf_tools::BPFProbeAttachType;
using bpf_tools::UProbeSpec;
using bpf_tools::WrappedBCCArrayTable;
using bpf_tools::WrappedBCCMap;
using bpf_tools::WrappedBCCStackTable;

uint64_t CountOpenFileDescriptors() {
    uint64_t count = 0;
    for (const auto& entry : std::filesystem::directory_iterator("/proc/self/fd")) {
        if (entry.is_symlink()) {
            ++count;
        }
    }
    return count;
}

std::string readSymbolicLink(const std::string& linkPath) {
    char path[PATH_MAX];
    ssize_t len = ::readlink(linkPath.c_str(), path, sizeof(path)-1);
    if (len != -1) {
        path[len] = '\0';
        return std::string(path);
    }
    return "";
}

class BasicRecorderTest : public ::testing::Test {
 public:
  BasicRecorderTest() {}

 protected:
  void SetUp() override {
    LOG(INFO) << absl::Substitute("Starting FD count: $0", CountOpenFileDescriptors());
    bcc_ = std::make_unique<bpf_tools::BCCWrapperImpl>();

    // Register our BPF program in the kernel, for real (recording), and for fake (replaying).
    ASSERT_OK(bcc_->InitBPFProgram(rr_test_bcc_script));
    LOG(INFO) << absl::Substitute("Post InitBPFProgram FD count: $0", CountOpenFileDescriptors());

    // const int64_t self_pid = getpid();
    const std::filesystem::path other_program_path = "/home/bkilimnik/pixie-privy/src/stirling/bpf_tools/rr/other-program";
    LOG(INFO) << "Path to other program: " << other_program_path.string();
    // /proc/<other-program-pid>/root/normal/path/to/binary
    const std::filesystem::path proc_other_program_path = "/proc/" + std::to_string(FLAGS_other_program_pid) + "/root" + other_program_path.string();
    LOG(INFO) << "Path to other program in proc: " << proc_other_program_path.string();
    LOG(INFO) << "Resolved path of symbolic link: " << readSymbolicLink("/proc/" + std::to_string(FLAGS_other_program_pid) + "/root");

    UProbeSpec kFooUprobe;
    kFooUprobe.binary_path = proc_other_program_path;
    // kFooUprobe.binary_path = other_program_path;
    kFooUprobe.pid = FLAGS_other_program_pid;
    kFooUprobe.symbol = "_Z3Foov";
    kFooUprobe.attach_type = BPFProbeAttachType::kEntry;
    kFooUprobe.probe_fn = "count_invocations";

    // Attach uprobes for this test case:
    LOG(INFO) << absl::Substitute("Pre AttachUProbe FD count: $0", CountOpenFileDescriptors());
    ASSERT_OK(bcc_->AttachUProbe(kFooUprobe));
    LOG(INFO) << absl::Substitute("Post AttachUProbe FD count: $0", CountOpenFileDescriptors());
  }

  void TearDown() override {
    bcc_->Close();
  }

  std::unique_ptr<bpf_tools::BCCWrapperImpl> bcc_;
};

TEST_F(BasicRecorderTest, BPFArrayRRTest) {

  LOG(INFO) << "other_program_pid: " << FLAGS_other_program_pid;
  auto bpf_array = WrappedBCCArrayTable<int>::Create(bcc_.get(), "state");
  LOG(INFO) << "Sleeping for 5.";
  sleep(5);
  int x = bpf_array->GetValue(0).ValueOrDie();
  LOG(INFO) << x;
  LOG(INFO) << "Pre Close FD count: " << CountOpenFileDescriptors();
  bcc_->Close();
  LOG(INFO) << "Post Close FD count (should be pre close count - 2): " << CountOpenFileDescriptors();
}

}  // namespace stirling
}  // namespace px
