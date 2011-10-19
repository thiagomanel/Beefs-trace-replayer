#include "../src/loader.h"
#include "gtest/gtest.h"
#include <stdlib.h>


TEST(LoaderTest, EmptyInputFile) {
    struct replay_workload rep_wld;
    FILE * input_f = fopen("tests/empty_input", "r");
    int ret = load(&rep_wld, input_f);
    EXPECT_EQ(0, ret);
    //TODO: test 0 cmds
    fclose(input_f);
}
