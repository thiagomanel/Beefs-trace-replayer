#include <check.h>
#include "../src/loader.h"
#include <stdio.h>
#include <stdlib.h>

START_TEST (test_loading_empty_file) {

  struct replay_command rep_cmd;
  FILE *input_f = fopen("empty_input", "r");

  int ret = load(rep_cmd, input_f);
  
  fail_unless (ret == 0, "Empty file loading finished properly");
  //TODO: test 0 cmds
  free (rep_cmd);//Free it properly
}
END_TEST

int main (void) {
  return 0;
}

Suite * money_suite (void)
{
  Suite *s = suite_create ("Money");

  /* Core test case */
  TCase *tc_core = tcase_create ("Core");
  tcase_add_test (tc_core, test_money_create);
  suite_add_tcase (s, tc_core);

  return s;
}

int  main (void)
{
  int number_failed;
  Suite *s = money_suite ();
  SRunner *sr = srunner_create (s);
  srunner_run_all (sr, CK_NORMAL);
  number_failed = srunner_ntests_failed (sr);
  srunner_free (sr);
  return (number_failed == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}
