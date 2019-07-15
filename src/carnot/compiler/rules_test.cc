#include <gmock/gmock.h>
#include <gtest/gtest.h>

#include <utility>
#include <vector>

#include <pypa/parser/parser.hh>

#include "src/carnot/compiler/ir_nodes.h"
#include "src/carnot/compiler/rules.h"
#include "src/carnot/compiler/test_utils.h"
#include "src/carnot/udf_exporter/udf_exporter.h"

namespace pl {
namespace carnot {
namespace compiler {

using testing::_;

class RulesTest : public ::testing::Test {
 protected:
  void SetUp() override {
    ::testing::Test::SetUp();
    info_ = udfexporter::ExportUDFInfo().ConsumeValueOrDie();

    auto rel_map = std::make_unique<RelationMap>();
    cpu_relation = table_store::schema::Relation(
        std::vector<types::DataType>({types::DataType::INT64, types::DataType::FLOAT64,
                                      types::DataType::FLOAT64, types::DataType::FLOAT64}),
        std::vector<std::string>({"count", "cpu0", "cpu1", "cpu2"}));
    rel_map->emplace("cpu", cpu_relation);

    compiler_state_ = std::make_unique<CompilerState>(std::move(rel_map), info_.get(), time_now);
    ast = MakeTestAstPtr();
    graph = std::make_shared<IR>();
    data_rule = std::make_shared<DataTypeRule>(compiler_state_.get());
  }
  pypa::AstPtr ast;
  std::shared_ptr<IR> graph;
  std::shared_ptr<Rule> data_rule;
  std::unique_ptr<CompilerState> compiler_state_;
  std::unique_ptr<RegistryInfo> info_;
  int64_t time_now = 1552607213931245000;
  table_store::schema::Relation cpu_relation;
};
class DataTypeRuleTest : public RulesTest {
 protected:
  void SetUp() override {
    RulesTest::SetUp();
    mem_src = graph->MakeNode<MemorySourceIR>().ValueOrDie();
    PL_CHECK_OK(mem_src->SetRelation(cpu_relation));
  }
  MemorySourceIR* mem_src;
};

// Simple map function.
TEST_F(DataTypeRuleTest, map_function) {
  auto map = graph->MakeNode<MapIR>().ValueOrDie();
  auto constant = graph->MakeNode<IntIR>().ValueOrDie();
  EXPECT_OK(constant->Init(10, ast));
  auto col = graph->MakeNode<ColumnIR>().ValueOrDie();
  EXPECT_OK(col->Init("count", ast));
  auto func = graph->MakeNode<FuncIR>().ValueOrDie();
  auto lambda = graph->MakeNode<LambdaIR>().ValueOrDie();
  EXPECT_OK(func->Init({FuncIR::Opcode::add, "+", "add"}, "pl",
                       std::vector<ExpressionIR*>({constant, col}), false /* compile_time */, ast));
  EXPECT_OK(lambda->Init({"col_name"}, func, ast));
  ArgMap amap({{"fn", lambda}});
  EXPECT_OK(map->Init(mem_src, amap, ast));

  // No rule has been run, don't expect any of these to be evaluated.
  EXPECT_FALSE(func->IsDataTypeEvaluated());
  EXPECT_FALSE(col->IsDataTypeEvaluated());

  // Expect the data_rule to change something.
  auto result = data_rule->Execute(graph.get());
  ASSERT_OK(result);
  EXPECT_TRUE(result.ValueOrDie());

  // Function shouldn't be updated, it had unresolved dependencies.
  EXPECT_FALSE(func->IsDataTypeEvaluated());
  // Column should be updated, it had unresolved dependencies.
  EXPECT_TRUE(col->IsDataTypeEvaluated());

  // Expect the data_rule to change something.
  result = data_rule->Execute(graph.get());
  ASSERT_OK(result);
  EXPECT_TRUE(result.ValueOrDie());

  // The function should now be evaluated, the column should stay evaluated.
  EXPECT_TRUE(func->IsDataTypeEvaluated());
  EXPECT_TRUE(col->IsDataTypeEvaluated());

  // Both should be integers.
  EXPECT_EQ(col->EvaluatedDataType(), types::DataType::INT64);
  EXPECT_EQ(func->EvaluatedDataType(), types::DataType::INT64);

  // Expect the data_rule to do nothing, no more work left.
  result = data_rule->Execute(graph.get());
  ASSERT_OK(result);
  EXPECT_FALSE(result.ValueOrDie());

  // Both should stay evaluated.
  EXPECT_TRUE(func->IsDataTypeEvaluated());
  EXPECT_TRUE(col->IsDataTypeEvaluated());
}

// The DataType shouldn't be resolved for compiler functions. They should be handled with a
// different rule.
TEST_F(DataTypeRuleTest, compiler_function_no_match) {
  // Compiler function should not get resolved.
  auto range = graph->MakeNode<RangeIR>().ValueOrDie();
  auto constant1 = graph->MakeNode<IntIR>().ValueOrDie();
  EXPECT_OK(constant1->Init(10, ast));
  auto constant2 = graph->MakeNode<IntIR>().ValueOrDie();
  EXPECT_OK(constant2->Init(12, ast));
  auto constant3 = graph->MakeNode<IntIR>().ValueOrDie();
  EXPECT_OK(constant3->Init(24, ast));
  auto func2 = graph->MakeNode<FuncIR>().ValueOrDie();
  EXPECT_OK(func2->Init({FuncIR::Opcode::add, "+", "add"}, "plc",
                        std::vector<ExpressionIR*>({constant1, constant2}), true /* compile_time */,
                        ast));
  EXPECT_OK(range->Init(mem_src, func2, constant3, ast));

  // No rule has been run, don't expect any of these to be evaluated.
  EXPECT_FALSE(func2->IsDataTypeEvaluated());
  // Expect the data_rule to do nothing, compiler function shouldn't be matched.
  auto result = data_rule->Execute(graph.get());
  ASSERT_OK(result);
  EXPECT_FALSE(result.ValueOrDie());
  // No rule has been run, don't expect any of these to be evaluated.
  EXPECT_FALSE(func2->IsDataTypeEvaluated());
}

// The rule should fail when an expression doesn't have a parent.
TEST_F(DataTypeRuleTest, function_no_parent) {
  // Compiler function should not get resolved.
  auto constant = graph->MakeNode<IntIR>().ValueOrDie();
  EXPECT_OK(constant->Init(10, ast));
  auto col = graph->MakeNode<ColumnIR>().ValueOrDie();
  EXPECT_OK(col->Init("count", ast));
  auto func = graph->MakeNode<FuncIR>().ValueOrDie();
  auto lambda = graph->MakeNode<LambdaIR>().ValueOrDie();
  EXPECT_OK(func->Init({FuncIR::Opcode::add, "+", "add"}, "pl",
                       std::vector<ExpressionIR*>({constant, col}), false /* compile_time */, ast));
  EXPECT_OK(lambda->Init({"col_name"}, func, ast));

  // Expect the data_rule to fail, with parents not found.
  auto result = data_rule->Execute(graph.get());
  EXPECT_NOT_OK(result);
}

// The DataType shouldn't be resolved for a function without a name.
TEST_F(DataTypeRuleTest, missing_udf_name) {
  auto map = graph->MakeNode<MapIR>().ValueOrDie();
  auto constant = graph->MakeNode<IntIR>().ValueOrDie();
  EXPECT_OK(constant->Init(10, ast));
  auto col = graph->MakeNode<ColumnIR>().ValueOrDie();
  EXPECT_OK(col->Init("count", ast));
  auto func = graph->MakeNode<FuncIR>().ValueOrDie();
  auto lambda = graph->MakeNode<LambdaIR>().ValueOrDie();
  EXPECT_OK(func->Init({FuncIR::Opcode::add, "+", "gobeldy"}, "pl",
                       std::vector<ExpressionIR*>({constant, col}), false /* compile_time */, ast));
  EXPECT_OK(lambda->Init({"col_name"}, func, ast));
  ArgMap amap({{"fn", lambda}});
  EXPECT_OK(map->Init(mem_src, amap, ast));

  // Expect the data_rule to successfully change columnir.
  auto result = data_rule->Execute(graph.get());
  EXPECT_OK(result);
  EXPECT_TRUE(result.ValueOrDie());

  // Expect the data_rule to change something.
  result = data_rule->Execute(graph.get());
  EXPECT_NOT_OK(result);

  // The function should not be evaluated, the function was not matched.
  EXPECT_FALSE(func->IsDataTypeEvaluated());
}

// Checks to make sure that agg functions work properly.
TEST_F(DataTypeRuleTest, function_in_agg) {
  auto map = graph->MakeNode<BlockingAggIR>().ValueOrDie();
  auto col = graph->MakeNode<ColumnIR>().ValueOrDie();
  EXPECT_OK(col->Init("count", ast));
  auto func = graph->MakeNode<FuncIR>().ValueOrDie();
  auto lambda = graph->MakeNode<LambdaIR>().ValueOrDie();
  EXPECT_OK(func->Init({FuncIR::Opcode::non_op, "", "mean"}, "pl",
                       std::vector<ExpressionIR*>({col}), false /* compile_time */, ast));
  EXPECT_OK(lambda->Init({col->col_name()}, func, ast));
  ArgMap amap({{"fn", lambda}, {"by", nullptr}});
  EXPECT_OK(map->Init(mem_src, amap, ast));

  // Expect the data_rule to successfully evaluate the column.
  auto result = data_rule->Execute(graph.get());
  EXPECT_OK(result);
  EXPECT_TRUE(result.ValueOrDie());

  EXPECT_TRUE(col->IsDataTypeEvaluated());
  EXPECT_FALSE(func->IsDataTypeEvaluated());

  // Expect the data_rule to change the function.
  result = data_rule->Execute(graph.get());
  ASSERT_OK(result);
  EXPECT_TRUE(result.ValueOrDie());

  // The function should be evaluated.
  EXPECT_TRUE(func->IsDataTypeEvaluated());
  EXPECT_EQ(func->EvaluatedDataType(), types::DataType::FLOAT64);
}

// Checks to make sure that nested functions are evaluated as expected.
TEST_F(DataTypeRuleTest, nested_functions) {
  auto map = graph->MakeNode<MapIR>().ValueOrDie();
  auto constant = graph->MakeNode<IntIR>().ValueOrDie();
  EXPECT_OK(constant->Init(10, ast));
  auto constant2 = graph->MakeNode<IntIR>().ValueOrDie();
  EXPECT_OK(constant2->Init(12, ast));
  auto col = graph->MakeNode<ColumnIR>().ValueOrDie();
  EXPECT_OK(col->Init("count", ast));
  auto func = graph->MakeNode<FuncIR>().ValueOrDie();
  auto func2 = graph->MakeNode<FuncIR>().ValueOrDie();
  auto lambda = graph->MakeNode<LambdaIR>().ValueOrDie();
  EXPECT_OK(func->Init({FuncIR::Opcode::add, "+", "add"}, "pl",
                       std::vector<ExpressionIR*>({constant, col}), false /* compile_time */, ast));

  EXPECT_OK(func2->Init({FuncIR::Opcode::add, "-", "subtract"}, "pl",
                        std::vector<ExpressionIR*>({constant2, func}), false /* compile_time */,
                        ast));
  EXPECT_OK(lambda->Init({"col_name"}, func2, ast));
  ArgMap amap({{"fn", lambda}});
  EXPECT_OK(map->Init(mem_src, amap, ast));

  // No rule has been run, don't expect any of these to be evaluated.
  EXPECT_FALSE(func->IsDataTypeEvaluated());
  EXPECT_FALSE(func2->IsDataTypeEvaluated());
  EXPECT_FALSE(col->IsDataTypeEvaluated());

  // Expect the data_rule to change something.
  auto result = data_rule->Execute(graph.get());
  ASSERT_OK(result);
  EXPECT_TRUE(result.ValueOrDie());

  // Functions shouldn't be updated, they have unresolved dependencies.
  EXPECT_FALSE(func->IsDataTypeEvaluated());
  EXPECT_FALSE(func2->IsDataTypeEvaluated());
  // Column should be updated, it had no dependencies.
  EXPECT_TRUE(col->IsDataTypeEvaluated());

  // Expect the data_rule to change something.
  result = data_rule->Execute(graph.get());
  ASSERT_OK(result);
  EXPECT_TRUE(result.ValueOrDie());

  // func1 should now be evaluated, the column should stay evaluated, func2 is not evaluated.
  EXPECT_TRUE(func->IsDataTypeEvaluated());
  EXPECT_FALSE(func2->IsDataTypeEvaluated());
  EXPECT_TRUE(col->IsDataTypeEvaluated());

  // Everything should be evaluated, func2 changes.
  result = data_rule->Execute(graph.get());
  ASSERT_OK(result);
  EXPECT_TRUE(result.ValueOrDie());

  // All should be evaluated.
  EXPECT_TRUE(func->IsDataTypeEvaluated());
  EXPECT_TRUE(func2->IsDataTypeEvaluated());
  EXPECT_TRUE(col->IsDataTypeEvaluated());

  // All should be integers.
  EXPECT_EQ(col->EvaluatedDataType(), types::DataType::INT64);
  EXPECT_EQ(func->EvaluatedDataType(), types::DataType::INT64);
  EXPECT_EQ(func2->EvaluatedDataType(), types::DataType::INT64);

  // Expect the data_rule to do nothing, no more work left.
  result = data_rule->Execute(graph.get());
  ASSERT_OK(result);
  EXPECT_FALSE(result.ValueOrDie());
}
// TODO(philkuz) try nested functions in the setup.

class SourceRelationTest : public RulesTest {
 protected:
  void SetUp() override { RulesTest::SetUp(); }
};

// Simple check with select all.
TEST_F(SourceRelationTest, set_source_select_all) {
  StringIR* table_str_node = graph->MakeNode<StringIR>().ValueOrDie();
  ASSERT_OK(table_str_node->Init("cpu", ast));

  MemorySourceIR* mem_src = graph->MakeNode<MemorySourceIR>().ValueOrDie();
  ArgMap memsrc_argmap({{"table", table_str_node}, {"select", nullptr}});
  EXPECT_OK(mem_src->Init(nullptr, memsrc_argmap, ast));

  EXPECT_FALSE(mem_src->IsRelationInit());

  SourceRelationRule source_relation_rule(compiler_state_.get());
  auto result = source_relation_rule.Execute(graph.get());
  ASSERT_OK(result);
  EXPECT_TRUE(result.ValueOrDie());
  EXPECT_TRUE(mem_src->IsRelationInit());
  // Make sure the relations are the same after processing.
  table_store::schema::Relation relation = mem_src->relation();
  EXPECT_TRUE(relation.col_types() == cpu_relation.col_types());
  EXPECT_TRUE(relation.col_names() == cpu_relation.col_names());
}

TEST_F(SourceRelationTest, set_source_variable_columns) {
  std::vector<std::string> str_columns = {"cpu1", "cpu2"};
  StringIR* table_str_node = graph->MakeNode<StringIR>().ValueOrDie();
  std::vector<IRNode*> select_columns;
  for (const std::string& c : str_columns) {
    auto select_col = graph->MakeNode<StringIR>().ValueOrDie();
    EXPECT_OK(select_col->Init(c, ast));
    select_columns.push_back(select_col);
  }
  auto select_list = graph->MakeNode<ListIR>().ValueOrDie();
  EXPECT_OK(select_list->Init(ast, select_columns));
  ASSERT_OK(table_str_node->Init("cpu", ast));

  MemorySourceIR* mem_src = graph->MakeNode<MemorySourceIR>().ValueOrDie();
  ArgMap memsrc_argmap({{"table", table_str_node}, {"select", select_list}});
  EXPECT_OK(mem_src->Init(nullptr, memsrc_argmap, ast));

  EXPECT_FALSE(mem_src->IsRelationInit());

  SourceRelationRule source_relation_rule(compiler_state_.get());
  auto result = source_relation_rule.Execute(graph.get());
  ASSERT_OK(result);
  EXPECT_TRUE(result.ValueOrDie());
  EXPECT_TRUE(mem_src->IsRelationInit());
  // Make sure the relations are the same after processing.
  table_store::schema::Relation relation = mem_src->relation();
  auto sub_relation_result = cpu_relation.MakeSubRelation(str_columns);
  EXPECT_OK(sub_relation_result);
  table_store::schema::Relation expected_relation = sub_relation_result.ValueOrDie();
  EXPECT_TRUE(relation.col_types() == expected_relation.col_types());
  EXPECT_TRUE(relation.col_names() == expected_relation.col_names());
}

TEST_F(SourceRelationTest, missing_table_name) {
  StringIR* table_str_node = graph->MakeNode<StringIR>().ValueOrDie();
  std::string table_name = "not_a_real_table_name";
  ASSERT_OK(table_str_node->Init(table_name, ast));

  MemorySourceIR* mem_src = graph->MakeNode<MemorySourceIR>().ValueOrDie();
  ArgMap memsrc_argmap({{"table", table_str_node}, {"select", nullptr}});
  EXPECT_OK(mem_src->Init(nullptr, memsrc_argmap, ast));

  EXPECT_FALSE(mem_src->IsRelationInit());

  SourceRelationRule source_relation_rule(compiler_state_.get());
  auto result = source_relation_rule.Execute(graph.get());
  EXPECT_NOT_OK(result);
  std::string error_string = absl::Substitute("Table '$0' not found.", table_name);
  EXPECT_TRUE(StatusHasCompilerError(result.status(), error_string));
}

TEST_F(SourceRelationTest, missing_columns) {
  std::string missing_column = "blah_column";
  std::vector<std::string> str_columns = {"cpu1", "cpu2", missing_column};
  StringIR* table_str_node = graph->MakeNode<StringIR>().ValueOrDie();
  std::vector<IRNode*> select_columns;
  for (const std::string& c : str_columns) {
    auto select_col = graph->MakeNode<StringIR>().ValueOrDie();
    EXPECT_OK(select_col->Init(c, ast));
    select_columns.push_back(select_col);
  }
  auto select_list = graph->MakeNode<ListIR>().ValueOrDie();
  EXPECT_OK(select_list->Init(ast, select_columns));
  ASSERT_OK(table_str_node->Init("cpu", ast));

  MemorySourceIR* mem_src = graph->MakeNode<MemorySourceIR>().ValueOrDie();
  ArgMap memsrc_argmap({{"table", table_str_node}, {"select", select_list}});
  EXPECT_OK(mem_src->Init(nullptr, memsrc_argmap, ast));

  EXPECT_FALSE(mem_src->IsRelationInit());

  SourceRelationRule source_relation_rule(compiler_state_.get());
  auto result = source_relation_rule.Execute(graph.get());
  EXPECT_NOT_OK(result);
  VLOG(1) << result.status().ToString();

  std::string error_string = absl::Substitute("Columns {$0} are missing in table.", missing_column);
  EXPECT_TRUE(StatusHasCompilerError(result.status(), error_string));
}
}  // namespace compiler
}  // namespace carnot
}  // namespace pl
