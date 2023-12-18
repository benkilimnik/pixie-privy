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

#include <fcntl.h>
#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include <sys/types.h>
#include <unistd.h>
#include <string_view>
#include <thread>

#include <magic_enum.hpp>

#include "src/common/fs/temp_file.h"
#include "src/common/system/clock.h"
#include "src/common/system/tcp_socket.h"
#include "src/common/system/udp_socket.h"
#include "src/common/system/unix_socket.h"
#include "src/shared/metadata/metadata.h"
#include "src/shared/types/column_wrapper.h"
#include "src/shared/types/types.h"
#include "src/stirling/core/data_table.h"
#include "src/stirling/source_connectors/socket_tracer/bcc_bpf_intf/socket_trace.hpp"
#include "src/stirling/source_connectors/socket_tracer/socket_trace_connector.h"
#include "src/stirling/source_connectors/socket_tracer/testing/client_server_system.h"
#include "src/stirling/source_connectors/socket_tracer/testing/socket_trace_bpf_test_fixture.h"
#include "src/stirling/testing/common.h"
#include <iostream>
#include <filesystem>
#include <system_error>

namespace px {
namespace stirling {

using ::px::stirling::testing::FindRecordsMatchingPID;
using ::px::stirling::testing::RecordBatchSizeIs;
using ::px::system::TCPSocket;
using ::px::system::UDPSocket;
using ::px::system::UnixSocket;
using ::px::types::ColumnWrapperRecordBatch;
using ::testing::Contains;
using ::testing::HasSubstr;
using ::testing::StrEq;

uint64_t CountOpenFileDescriptors() {
    uint64_t count = 0;
    for (const auto& entry : std::filesystem::directory_iterator("/proc/self/fd")) {
        if (entry.is_symlink()) {
            ++count;
        }
    }
    return count;
}

constexpr std::string_view kHTTPReqMsg1 =
    "GET /endpoint1 HTTP/1.1\r\n"
    "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0\r\n"
    "\r\n";

// constexpr std::string_view kHTTPReqMsg2 =
//     "GET /endpoint2 HTTP/1.1\r\n"
//     "User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0\r\n"
//     "\r\n";

// constexpr std::string_view kHTTPRespMsg1 =
//     "HTTP/1.1 200 OK\r\n"
//     "Content-Type: application/json; msg1\r\n"
//     "Content-Length: 0\r\n"
//     "\r\n";

// constexpr std::string_view kHTTPRespMsg2 =
//     "HTTP/1.1 200 OK\r\n"
//     "Content-Type: application/json; msg2\r\n"
//     "Content-Length: 0\r\n"
//     "\r\n";

// TODO(yzhao): Apply this pattern to other syscall pairs. An issue is that other syscalls do not
// use scatter buffer. One approach would be to concatenate inner vector to a single string, and
// then feed to the syscall. Another caution is that value-parameterized tests actually discourage
// changing functions being tested according to test parameters. The canonical pattern is using test
// parameters as inputs, but keep the function being tested fixed.
enum class SyscallPair {
  kSendRecv,
  kWriteRead,
  kSendMsgRecvMsg,
  kSendMMsgRecvMMsg,
  kWritevReadv,
};

struct SocketTraceBPFTestParams {
  SyscallPair syscall_pair;
  uint64_t trace_role;
};

class SocketTraceBPFTest
    : public testing::SocketTraceBPFTestFixture</* TClientSideTracing */ true> {
 protected:
  StatusOr<const ConnTracker*> GetConnTracker(int pid, int fd) {
    PX_ASSIGN_OR_RETURN(const ConnTracker* tracker, source_->GetConnTracker(pid, fd));
    if (tracker == nullptr) {
      return error::Internal("No ConnTracker found for pid=$0 fd=$1", pid, fd);
    }
    return tracker;
  }

  StatusOr<ConnTracker*> GetMutableConnTracker(int pid, int fd) {
    conn_id_t conn_id;
    conn_id.tsid = 0;
    for (const auto* conn_tracker : source_->conn_trackers_mgr_.active_trackers()) {
      if (conn_tracker->conn_id().upid.pid == static_cast<uint32_t>(pid) &&
          conn_tracker->conn_id().fd == fd) {
        conn_id = conn_tracker->conn_id();
        break;
      }
    }
    // If tsid=0 then the above loop didn't find any conn trackers with the same {pid, fd} pair.
    if (conn_id.tsid == 0) {
      return error::Internal("No ConnTracker found for pid=$0 fd=$1", pid, fd);
    }
    auto& conn_tracker = source_->GetOrCreateConnTracker(conn_id);
    return &conn_tracker;
  }
};

TEST(SocketTraceBPFTest, SimpleFDCountTest) {
    uint64_t initial_fd_count = CountOpenFileDescriptors();
    EXPECT_EQ(initial_fd_count, 6);


    uint64_t final_fd_count = CountOpenFileDescriptors();
    EXPECT_EQ(final_fd_count, 6);
}

TEST_F(SocketTraceBPFTest, LargeMessages) {
  ConfigureBPFCapture(traffic_protocol_t::kProtocolHTTP, kRoleClient | kRoleServer);

  std::string large_response =
      "HTTP/1.1 200 OK\r\n"
      "Content-Type: application/json; msg2\r\n"
      "Content-Length: 131072\r\n"
      "\r\n";
  large_response += std::string(131072, '+');

  testing::SendRecvScript script({
      {{kHTTPReqMsg1}, {large_response}},
  });

  testing::ClientServerSystem system;
  system.RunClientServer<&TCPSocket::Recv, &TCPSocket::Send>(script);

  source_->BCC().PollPerfBuffers();

  ASSERT_OK_AND_ASSIGN(auto* client_tracker,
                       GetMutableConnTracker(system.ClientPID(), system.ClientFD()));
  EXPECT_EQ(client_tracker->send_data().data_buffer().Head(), kHTTPReqMsg1);
  std::string client_recv_data(client_tracker->recv_data().data_buffer().Head());
  EXPECT_THAT(client_recv_data.size(), 131153);
  EXPECT_THAT(client_recv_data, HasSubstr("+++++"));
  EXPECT_EQ(client_recv_data.substr(client_recv_data.size() - 5, 5), "+++++");

  // The server's send syscall transmits all 131153 bytes in one shot.
  // This is over the limit that we can transmit through BPF, and so we expect
  // filler bytes on this side of the connection. Note that the client doesn't have the
  // same behavior, because the recv syscall provides the data in chunks.
  ASSERT_OK_AND_ASSIGN(auto* server_tracker,
                       GetMutableConnTracker(system.ServerPID(), system.ServerFD()));
  EXPECT_EQ(server_tracker->recv_data().data_buffer().Head(), kHTTPReqMsg1);
  std::string server_send_data(server_tracker->send_data().data_buffer().Head());
  EXPECT_THAT(server_send_data.size(), 131153);
  EXPECT_THAT(server_send_data, HasSubstr("+++++"));
  // We expect filling with \0 bytes.
  EXPECT_EQ(server_send_data.substr(server_send_data.size() - 5, 5), ConstStringView("\0\0\0\0\0"));
}

INSTANTIATE_TEST_SUITE_P(FDLeakSuite, SocketTraceBPFTest, ::testing::Values(SocketTraceBPFTestParams{
    .syscall_pair = SyscallPair::kSendRecv,
    .trace_role = kRoleClient | kRoleServer,
}));

}  // namespace stirling
}  // namespace px
