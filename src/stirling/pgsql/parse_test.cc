#include "src/stirling/pgsql/parse.h"

#include <string>
#include <utility>

#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include "src/common/base/base.h"
#include "src/common/base/test_utils.h"

namespace pl {
namespace stirling {
namespace pgsql {

using ::testing::AllOf;
using ::testing::ElementsAre;
using ::testing::Field;
using ::testing::IsEmpty;

template <typename TagMatcher, typename LengthType, typename PayloadMatcher>
auto IsRegularMessage(TagMatcher tag, LengthType len, PayloadMatcher payload) {
  return AllOf(Field(&RegularMessage::tag, tag), Field(&RegularMessage::len, len),
               Field(&RegularMessage::payload, payload));
}

template <typename PayloadMatcher>
auto HasPayloads(PayloadMatcher req_payload, PayloadMatcher resp_payload) {
  return AllOf(Field(&Record::req, Field(&RegularMessage::payload, req_payload)),
               Field(&Record::resp, Field(&RegularMessage::payload, resp_payload)));
}

const std::string_view kQueryTestData =
    CreateStringView<char>("Q\000\000\000\033select * from account;\000");
const std::string_view kStartupMsgTestData = CreateStringView<char>(
    "\x00\x00\x00\x54\x00\003\x00\x00user\x00postgres\x00"
    "database\x00postgres\x00"
    "application_name\x00psql\x00"
    "client_encoding\x00UTF8\x00\x00");

TEST(PGSQLParseTest, BasicMessage) {
  std::string_view data = kQueryTestData;
  RegularMessage msg = {};
  EXPECT_EQ(ParseState::kSuccess, ParseRegularMessage(&data, &msg));
  EXPECT_THAT(
      msg, IsRegularMessage(Tag::kQuery, 27, CreateStringView<char>("select * from account;\0")));
}

auto IsNV(std::string_view name, std::string_view value) {
  return AllOf(Field(&NV::name, name), Field(&NV::value, value));
}

TEST(PGSQLParseTest, StartupMessage) {
  std::string_view data = kStartupMsgTestData;
  StartupMessage msg = {};
  EXPECT_EQ(ParseState::kSuccess, ParseStartupMessage(&data, &msg));
  EXPECT_EQ(84, msg.len);
  EXPECT_EQ(3, msg.proto_ver.major);
  EXPECT_EQ(0, msg.proto_ver.minor);
  EXPECT_THAT(msg.nvs,
              ElementsAre(IsNV("user", "postgres"), IsNV("database", "postgres"),
                          IsNV("application_name", "psql"), IsNV("client_encoding", "UTF8")));
  EXPECT_THAT(data, IsEmpty());
}

const std::string_view kRowDescTestData = CreateStringView<char>(
    "T\000\000\000\246"
    "\000\006"
    "Name"
    "\000\000\000\004\356\000\002\000\000\000\023\000@\377\377\377\377\000\000"
    "Owner"
    "\000\000\000\000\000\000\000\000\000\000\023\000@\377\377\377\377\000\000"
    "Encoding"
    "\000\000\000\000\000\000\000\000\000\000\023\000@\377\377\377\377\000\000"
    "Collate"
    "\000\000\000\004\356\000\005\000\000\000\023\000@\377\377\377\377\000\000"
    "Ctype"
    "\000\000\000\004\356\000\006\000\000\000\023\000@\377\377\377\377\000\000"
    "Access "
    "privileges\000\000\000\000\000\000\000\000\000\000\031\377\377\377\377\377\377\000\000");

TEST(PGSQLParseTest, RowDesc) {
  std::string_view data = kRowDescTestData;
  RegularMessage msg = {};
  EXPECT_EQ(ParseState::kSuccess, ParseRegularMessage(&data, &msg));
  EXPECT_EQ(Tag::kRowDesc, msg.tag);
  EXPECT_EQ(166, msg.len);
  EXPECT_THAT(ParseRowDesc(msg.payload),
              ElementsAre("Name", "Owner", "Encoding", "Collate", "Ctype", "Access privileges"));
}

const std::string_view kDataRowTestData = CreateStringView<char>(
    "D"
    "\000\000\000F"
    "\000\006"
    "\000\000\000\010postgres"
    "\000\000\000\010postgres"
    "\000\000\000\004UTF8"
    "\000\000\000\nen_US.utf8"
    "\000\000\000\nen_US.utf8"
    "\377\377\377\377");

TEST(PGSQLParseTest, DataRow) {
  std::string_view data = kDataRowTestData;
  RegularMessage msg = {};
  EXPECT_EQ(ParseState::kSuccess, ParseRegularMessage(&data, &msg));
  EXPECT_EQ(Tag::kDataRow, msg.tag);
  EXPECT_EQ(70, msg.len);
  EXPECT_THAT(ParseDataRow(msg.payload), ElementsAre("postgres", "postgres", "UTF8", "en_US.utf8",
                                                     "en_US.utf8", std::nullopt));
}

TEST(PGSQLParseTest, AssembleQueryResp) {
  auto row_desc_data = kRowDescTestData;
  auto data_row_data = kDataRowTestData;

  RegularMessage m1 = {};
  RegularMessage m2 = {};
  RegularMessage m3 = {};
  m3.tag = Tag::kCmdComplete;
  m3.payload = "SELECT 1";

  EXPECT_EQ(ParseState::kSuccess, ParseRegularMessage(&row_desc_data, &m1));
  EXPECT_EQ(ParseState::kSuccess, ParseRegularMessage(&data_row_data, &m2));

  std::deque<RegularMessage> resps = {m1, m2, m3};

  auto begin = resps.begin();
  ASSERT_OK_AND_THAT(AssembleQueryResp(&begin, resps.end()),
                     Field(&RegularMessage::payload,
                           "Name,Owner,Encoding,Collate,Ctype,Access privileges\n"
                           "postgres,postgres,UTF8,en_US.utf8,en_US.utf8,[NULL]\n"
                           "SELECT 1"));
  EXPECT_EQ(begin, resps.end());
}

TEST(PGSQLParseTest, AssembleQueryRespFailures) {
  std::deque<RegularMessage> resps;
  auto begin = resps.begin();
  const auto end = resps.end();
  EXPECT_NOT_OK(AssembleQueryResp(&begin, end));
}

const std::string_view kReadyForQueryMsg = CreateStringView<char>("Z\000\000\000\005I");
const std::string_view kSyncMsg = CreateStringView<char>("S\000\000\000\004");

const std::string_view kParseMsg = CreateStringView<char>(
    // Parse
    "P"
    "\000\000\000\251"  // 169, payload is the next 165 bytes.
    "\000"
    "select t.oid, t.typname, t.typbasetype\n"
    "from pg_type t\n"
    "  join pg_type base_type on t.typbasetype=base_type.oid\n"
    "where t.typtype = \'d\'\n"
    "  and base_type.typtype = \'b\'\000\000\000"
    // kDesc
    "D\000\000\000\006S\000"
    // kSync
    "S\000\000\000\004"
    // kBind
    "B\000\000\000\020\000\000\000\000\000\000\000\002\000\001\000\001"
    // kExecute
    "E\000\000\000\011\000\000\000\000\000");

const std::string_view kParseRespMsg = CreateStringView<char>(
    // kParseComplete
    "1\000\000\000\004"
    // kParamDesc
    "t\000\000\000\006\000\000"
    // kRowDesc
    "T\000\000\000\124"
    // 3 fields
    "\000\003"
    "oid\000\000\000\004\337\377\376\000\000\000\032\000\004\377\377\377\377\000\000"
    "typname\000\000\000\004\337\000\001\000\000\000\023\000@\377\377\377\377\000\000"
    "typbasetype\000\000\000\004\337\000\030\000\000\000\032\000\004\377\377\377\377\000\000"
    // kReadyForQuery
    "Z\000\000\000\005I"
    // kBindComplete
    "2\000\000\000\004"
    // kDataRow
    "D\000\000\000)\000\003\000\000\000\004\000\0001\361\000\000\000\017cardinal_"
    "number\000\000\000\004\000\000\000\027"
    "D\000\000\000#\000\003\000\000\000\004\000\0001\375\000\000\000\tyes_or_"
    "no\000\000\000\004\000\000\004\023"
    "D\000\000\000(\000\003\000\000\000\004\000\0001\366\000\000\000\016sql_"
    "identifier\000\000\000\004\000\000\004\023"
    "D\000\000\000(\000\003\000\000\000\004\000\0001\364\000\000\000\016character_"
    "data\000\000\000\004\000\000\004\023"
    "D\000\000\000$\000\003\000\000\000\004\000\0001\373\000\000\000\ntime_"
    "stamp\000\000\000\004\000\000\004\240"
    // kCmdComplete
    "C\000\000\000\rSELECT 5\000");

StatusOr<std::deque<RegularMessage>> ParseRegularMessages(std::string_view data) {
  std::deque<RegularMessage> msgs;
  RegularMessage msg = {};
  while (ParseRegularMessage(&data, &msg) == ParseState::kSuccess) {
    msgs.push_back(std::move(msg));
  }
  if (!data.empty()) {
    return error::InvalidArgument("Some data are not parsed");
  }
  return msgs;
}

TEST(ProcessFramesTest, GetParseReqMsgs) {
  ASSERT_OK_AND_ASSIGN(std::deque<RegularMessage> reqs, ParseRegularMessages(kParseMsg));
  ASSERT_OK_AND_ASSIGN(std::deque<RegularMessage> resps, ParseRegularMessages(kParseRespMsg));

  RecordsWithErrorCount<pgsql::Record> records_and_err_count = ProcessFrames(&reqs, &resps);
  EXPECT_THAT(reqs, IsEmpty());
  EXPECT_THAT(resps, IsEmpty());
  EXPECT_NE(0, records_and_err_count.records.front().req.payload.size());
  EXPECT_THAT(records_and_err_count.records,
              ElementsAre(HasPayloads(
                  CreateStringView<char>("select t.oid, t.typname, t.typbasetype\n"
                                         "from pg_type t\n"
                                         "  join pg_type base_type on t.typbasetype=base_type.oid\n"
                                         "where t.typtype = 'd'\n"
                                         "  and base_type.typtype = 'b'"),
                  CreateStringView<char>("oid,typname,typbasetype\n"
                                         "\0\0\x31\xF1,cardinal_number,\0\0\0\x17\n"
                                         "\0\0\x31\xFD,yes_or_no,\0\0\x4\x13\n"
                                         "\0\0\x31\xF6,sql_identifier,\0\0\x4\x13\n"
                                         "\0\0\x31\xF4,character_data,\0\0\x4\x13\n"
                                         "\0\0\x31\xFB,time_stamp,\0\0\x4\xA0\nSELECT 5"))));
  EXPECT_EQ(0, records_and_err_count.error_count);
}

const std::string_view kCmdCompleteData = CreateStringView<char>("C\000\000\000\rSELECT 1\000");

TEST(ProcessFramesTest, MatchQueryAndRowDesc) {
  constexpr char kQueryText[] = "select * from table;";
  RegularMessage q = {};
  q.tag = Tag::kQuery;
  q.len = sizeof(kQueryText) + sizeof(int32_t);
  q.payload = kQueryText;

  std::string_view data = kRowDescTestData;
  RegularMessage t = {};
  EXPECT_EQ(ParseState::kSuccess, ParseRegularMessage(&data, &t));

  data = kDataRowTestData;
  RegularMessage d = {};
  EXPECT_EQ(ParseState::kSuccess, ParseRegularMessage(&data, &d));

  data = kCmdCompleteData;
  RegularMessage c = {};
  EXPECT_EQ(ParseState::kSuccess, ParseRegularMessage(&data, &c));

  std::deque<RegularMessage> reqs = {std::move(q)};
  std::deque<RegularMessage> resps = {std::move(t), std::move(d), std::move(c)};
  RecordsWithErrorCount<pgsql::Record> records_and_err_count = ProcessFrames(&reqs, &resps);
  EXPECT_THAT(reqs, IsEmpty());
  EXPECT_THAT(resps, IsEmpty());
  EXPECT_THAT(records_and_err_count.records,
              ElementsAre(HasPayloads("select * from table;",
                                      "Name,Owner,Encoding,Collate,Ctype,Access privileges\n"
                                      "postgres,postgres,UTF8,en_US.utf8,en_US.utf8,[NULL]\n"
                                      "SELECT 1")));
  EXPECT_EQ(0, records_and_err_count.error_count);
}

const std::string_view kDropTableCmplMsg =
    CreateStringView<char>("C\000\000\000\017DROP TABLE\000");

TEST(ProcessFramesTest, DropTable) {
  constexpr char kQueryText[] = "drop table foo;";
  RegularMessage q = {};
  q.tag = Tag::kQuery;
  q.len = sizeof(kQueryText) + sizeof(int32_t);
  q.payload = kQueryText;

  std::string_view data = kDropTableCmplMsg;
  RegularMessage c = {};
  EXPECT_EQ(ParseState::kSuccess, ParseRegularMessage(&data, &c));

  std::deque<RegularMessage> reqs = {std::move(q)};
  std::deque<RegularMessage> resps = {std::move(c)};
  RecordsWithErrorCount<pgsql::Record> records_and_err_count = ProcessFrames(&reqs, &resps);
  EXPECT_THAT(reqs, IsEmpty());
  EXPECT_THAT(resps, IsEmpty());
  EXPECT_THAT(records_and_err_count.records,
              ElementsAre(HasPayloads("drop table foo;", "DROP TABLE")));
  EXPECT_EQ(0, records_and_err_count.error_count);
}

const std::string_view kRollbackMsg =
    CreateStringView<char>("\x51\x00\x00\x00\x0d\x52\x4f\x4c\x4c\x42\x41\x43\x4b\x00");
const std::string_view kRollbackCmplMsg =
    CreateStringView<char>("\x43\x00\x00\x00\x0d\x52\x4f\x4c\x4c\x42\x41\x43\x4b\x00");

TEST(ProcessFramesTest, Rollback) {
  RegularMessage rollback_msg = {};
  std::string_view data = kRollbackMsg;
  EXPECT_EQ(ParseState::kSuccess, ParseRegularMessage(&data, &rollback_msg));

  RegularMessage cmpl_msg = {};
  data = kRollbackCmplMsg;
  EXPECT_EQ(ParseState::kSuccess, ParseRegularMessage(&data, &cmpl_msg));

  std::deque<RegularMessage> reqs = {std::move(rollback_msg)};
  std::deque<RegularMessage> resps = {std::move(cmpl_msg)};
  RecordsWithErrorCount<pgsql::Record> records_and_err_count = ProcessFrames(&reqs, &resps);
  EXPECT_THAT(reqs, IsEmpty());
  EXPECT_THAT(resps, IsEmpty());
  EXPECT_THAT(records_and_err_count.records, ElementsAre(HasPayloads("ROLLBACK", "ROLLBACK")));
  EXPECT_EQ(0, records_and_err_count.error_count);
}

TEST(FindFrameBoundaryTest, FindTag) {
  EXPECT_EQ(0, FindFrameBoundary(kDropTableCmplMsg, 0));
  EXPECT_EQ(0, FindFrameBoundary(kRowDescTestData, 0));
  EXPECT_EQ(0, FindFrameBoundary(kDataRowTestData, 0));
  const std::string data = absl::StrCat("aaaaa", kDataRowTestData);
  EXPECT_EQ(5, FindFrameBoundary(data, 0));
}

}  // namespace pgsql
}  // namespace stirling
}  // namespace pl
