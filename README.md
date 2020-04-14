# git-branch-name-jira-hook
Git Hook which extract the JIRA Ticket ID from the branch name and check against Jira.

Branch RegEx format is :
 ^(feature|bugfix|improvement|library|prerelease|release|hotfix)\/([a-zA-Z0-9-]+?)(\_)([a-zA-Z0-9._-]+?)$
## Examples:
1. feature/PRJ-123_Some_Definition -> correct
2. feature/PRJ-321_Some_Definition -> correct however if _PRJ-321_ status us done than it will give error
3. bug/PRJ-123_Some_Definition -> incorrect as it starts with _bug_ which is not in the regex
4. feature/SOME_TEXT -> incorrect as _SOME_ is not a correct Jira Ticket ID format
