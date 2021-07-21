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

#include "src/common/testing/test_utils/container_runner.h"
#include "src/common/testing/testing.h"
#include "src/stirling/source_connectors/socket_tracer/socket_trace_connector.h"
#include "src/stirling/source_connectors/socket_tracer/testing/socket_trace_bpf_test_fixture.h"

namespace px {
namespace stirling {

using ::px::stirling::testing::FindRecordIdxMatchesPID;
using ::px::testing::BazelBinTestFilePath;
using ::testing::AllOf;
using ::testing::Field;
using ::testing::HasSubstr;
using ::testing::UnorderedElementsAre;
// Automatically converts ToString() to stream operator for gtest.
using ::px::operator<<;

class NATSServerContainer : public ContainerRunner {
 public:
  NATSServerContainer()
      : ContainerRunner(BazelBinTestFilePath(kBazelImageTar), kContainerNamePrefix, kReadyMessage) {
  }

 private:
  static constexpr std::string_view kBazelImageTar =
      "src/stirling/source_connectors/socket_tracer/testing/containers/nats_image.tar";
  static constexpr std::string_view kContainerNamePrefix = "nats_server";
  static constexpr std::string_view kReadyMessage = "Server is ready";
};

class NATSClientContainer : public ContainerRunner {
 public:
  NATSClientContainer()
      : ContainerRunner(BazelBinTestFilePath(kBazelImageTar), kContainerNamePrefix, kReadyMessage) {
  }

 private:
  static constexpr std::string_view kBazelImageTar =
      "src/stirling/source_connectors/socket_tracer/protocols/nats/testing/"
      "nats_test_client_image.tar";
  static constexpr std::string_view kContainerNamePrefix = "nats_test_client";
  static constexpr std::string_view kReadyMessage = "";
};

class NATSTraceBPFTest : public testing::SocketTraceBPFTest</* TClientSideTracing */ false> {
 protected:
  NATSTraceBPFTest() {
    FLAGS_stirling_enable_nats_tracing = true;
    PL_CHECK_OK(server_container_.Run(std::chrono::seconds{150}));
  }

  NATSServerContainer server_container_;
  NATSClientContainer client_container_;
};

struct NATSTraceRecord {
  int64_t ts_ns;
  std::string cmd;
  std::string options;
  std::string resp;

  std::string ToString() const {
    return absl::Substitute("ts_ns=$0 cmd=$1 options=$2 resp=$3", ts_ns, cmd, options, resp);
  }
};

std::vector<NATSTraceRecord> GetNATSTraceRecords(
    const types::ColumnWrapperRecordBatch& record_batch, int pid) {
  std::vector<NATSTraceRecord> res;
  for (const auto& idx : FindRecordIdxMatchesPID(record_batch, nats_idx::kUPID, pid)) {
    res.push_back(
        NATSTraceRecord{record_batch[nats_idx::kTime]->Get<types::Time64NSValue>(idx).val,
                        std::string(record_batch[nats_idx::kCMD]->Get<types::StringValue>(idx)),
                        std::string(record_batch[nats_idx::kOptions]->Get<types::StringValue>(idx)),
                        std::string(record_batch[nats_idx::kResp]->Get<types::StringValue>(idx))});
  }
  return res;
}

auto EqualsNATSTraceRecord(std::string cmd, std::string options, std::string resp) {
  return AllOf(Field(&NATSTraceRecord::cmd, cmd),
               Field(&NATSTraceRecord::options, HasSubstr(options)),
               Field(&NATSTraceRecord::resp, resp));
}

// Tests that a series of commands issued by the test client were traced.
TEST_F(NATSTraceBPFTest, VerifyBatchedCommands) {
  StartTransferDataThread();

  client_container_.Run(
      std::chrono::seconds{10},
      {absl::Substitute("--network=container:$0", server_container_.container_name())});
  const int server_pid = server_container_.process_pid();

  client_container_.Wait();

  StopTransferDataThread();

  std::vector<TaggedRecordBatch> tablets = ConsumeRecords(SocketTraceConnector::kNATSTableNum);

  ASSERT_FALSE(tablets.empty());

  EXPECT_THAT(
      GetNATSTraceRecords(tablets[0].records, server_pid),
      UnorderedElementsAre(
          EqualsNATSTraceRecord(
              "CONNECT",
              R"({"verbose":false,"pedantic":false,"tls_required":false,"name":"",)"
              R"("lang":"go","version":"1.10.0","protocol":1,"echo":true})",
              ""),
          EqualsNATSTraceRecord("INFO", R"("host":"0.0.0.0","port":4222,"headers":true)", ""),
          EqualsNATSTraceRecord("SUB", R"({"sid":"1","subject":"foo"})", ""),
          EqualsNATSTraceRecord("MSG", R"({"payload":"Hello World","sid":"1","subject":"foo"})",
                                ""),
          EqualsNATSTraceRecord("PUB", R"({"payload":"Hello World","subject":"foo"})", ""),
          EqualsNATSTraceRecord("UNSUB", R"({"sid":"1"})", "")));
}

}  // namespace stirling
}  // namespace px