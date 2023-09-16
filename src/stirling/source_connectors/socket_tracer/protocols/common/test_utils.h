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

#pragma once

#include <deque>
#include <string>
#include <vector>

#include "src/common/base/base.h"
#include "src/stirling/source_connectors/socket_tracer/bcc_bpf_intf/socket_trace.hpp"
#include "src/stirling/source_connectors/socket_tracer/protocols/common/data_stream_buffer.h"

namespace px {
namespace stirling {
namespace protocols {

class DataStreamBufferTestWrapper {
 protected:
  static constexpr size_t kDataBufferSize = 128 * 1024;
  static constexpr size_t kMaxGapSize = 128 * 1024;
  static constexpr size_t kAllowBeforeGapSize = 128 * 1024;

  DataStreamBufferTestWrapper() : data_buffer_(kDataBufferSize, kMaxGapSize, kAllowBeforeGapSize) {}

  void AddEvent(const SocketDataEvent& event) {
    data_buffer_.Add(event.attr.pos, event.msg, event.attr.timestamp_ns);
  }

  void AddEvents(const std::vector<SocketDataEvent>& events) {
    for (const auto& e : events) {
      AddEvent(e);
    }
  }

  DataStreamBuffer data_buffer_;
};

template <typename TStrType>
std::vector<SocketDataEvent> CreateEvents(const std::vector<TStrType>& msgs) {
  std::vector<SocketDataEvent> events;
  size_t pos = 0;
  for (size_t i = 0; i < msgs.size(); ++i) {
    events.emplace_back();
    events.back().msg = msgs[i];
    events.back().attr.timestamp_ns = i;
    events.back().attr.pos = pos;
    events.back().attr.msg_size = msgs[i].size();
    pos += msgs[i].size();
  }
  return events;
}

template <typename TKey, typename TFrameType>
void initialize_map_deques(
  std::map<TKey, std::deque<TFrameType>*>* req_map,
  std::map<TKey, std::deque<TFrameType>*>* resp_map,
  size_t nkeys) {
  for (size_t i = 0; i < nkeys; ++i) {
    std::deque<TFrameType>* req_deque = new std::deque<TFrameType>();
    (*req_map)[i] = req_deque;
    std::deque<TFrameType>* resp_deque = new std::deque<TFrameType>();
    (*resp_map)[i] = resp_deque;
  }
}

template <typename TKey, typename TFrameType>
void free_map_deques(
  std::map<TKey, std::deque<TFrameType>*>* req_map,
  std::map<TKey, std::deque<TFrameType>*>* resp_map)
  {
  for (auto& key_value_pair: *req_map) {
    delete key_value_pair.second;
  }
  for (auto& key_value_pair: *resp_map) {
    delete key_value_pair.second;
  }
}

}  // namespace protocols
}  // namespace stirling
}  // namespace px