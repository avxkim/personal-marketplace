Automated QA testing from Redmine tickets. Reads ticket details, generates test plan, executes UI tests with multiple roles, and posts results.

## Workflow

When you invoke this command with a Redmine issue URL, follow these steps:

### 1. Locate Redmine Tool

```bash
REDMINE_TOOL=$(for path in $(jq -r 'to_entries[] | .value.installLocation + "/plugin/skills/redmine-admin/redmine-tool.sh"' ~/.claude/plugins/known_marketplaces.json); do [ -f "$path" ] && echo "$path" && break; done)
```

### 2. Extract Issue ID from URL

Extract the issue number from $ARGUMENTS using regex:

```bash
if [[ "$ARGUMENTS" =~ /issues/([0-9]+) ]]; then
  ISSUE_ID="${BASH_REMATCH[1]}"
else
  echo "ERROR: Invalid Redmine URL. Expected format: https://redmine.int-tro.kz/issues/XXX"
  exit 1
fi
```

### 3. Fetch Issue Details

Use the redmine-admin skill to get complete issue information:

```bash
ISSUE_JSON=$("$REDMINE_TOOL" get-issue "$ISSUE_ID")

SUBJECT=$(echo "$ISSUE_JSON" | jq -r '.issue.subject')
DESCRIPTION=$(echo "$ISSUE_JSON" | jq -r '.issue.description // ""')
TRACKER=$(echo "$ISSUE_JSON" | jq -r '.issue.tracker.name')
STATUS=$(echo "$ISSUE_JSON" | jq -r '.issue.status.name')
PRIORITY=$(echo "$ISSUE_JSON" | jq -r '.issue.priority.name')

JOURNALS=$(echo "$ISSUE_JSON" | jq -r '.issue.journals // [] | map(select(.notes != null and .notes != "")) | map(.notes) | join("\n\n---\n\n")')
```

### 4. Analyze Ticket for Test Requirements

Analyze the issue content to determine:

**A. Extract Test Environment:**

Search description and comments for environment URLs or keywords:

```bash
FULL_TEXT="$DESCRIPTION

$JOURNALS"

TEST_ENV="dev"
TEST_URL=""

if echo "$FULL_TEXT" | grep -qi "api\.goalta\.kz"; then
  TEST_ENV="production"
  TEST_URL="$ALTA_API_PROD_URL"
elif echo "$FULL_TEXT" | grep -qi "api-stage\.goalta\.kz"; then
  TEST_ENV="staging"
  TEST_URL="$ALTA_API_STAGE_URL"
elif echo "$FULL_TEXT" | grep -qi "api\.dev\.alta-api\.kz"; then
  TEST_ENV="dev"
  TEST_URL="$ALTA_API_DEV_URL"
else
  TEST_ENV="dev"
  TEST_URL="$ALTA_API_DEV_URL"
fi
```

**B. Determine if UI Testing is Required:**

Check for UI-related indicators:

```bash
NEEDS_UI_TEST=false

if echo "$FULL_TEXT" | grep -qiE "(ui|frontend|web|interface|screen|button|form|page|display|визуал|интерфейс)"; then
  NEEDS_UI_TEST=true
fi

if echo "$TRACKER" | grep -qiE "(Bug|Feature|Enhancement)"; then
  NEEDS_UI_TEST=true
fi

if echo "$ISSUE_JSON" | jq -e '.issue.attachments[] | select(.filename | test("\\.(png|jpg|jpeg|gif|webp)$"))' > /dev/null 2>&1; then
  NEEDS_UI_TEST=true
fi
```

### 5. Generate Test Checklist

Based on the ticket analysis, create a comprehensive test plan. Present this to the user:

```
## Test Plan for Issue #$ISSUE_ID: $SUBJECT

**Tracker**: $TRACKER | **Priority**: $PRIORITY | **Status**: $STATUS
**Environment**: $TEST_ENV ($TEST_URL)
**UI Testing Required**: $NEEDS_UI_TEST

### Test Scope

$DESCRIPTION

### Test Roles

1. **Superadmin** - Full system access
   - Username: $ALTA_TEST_SUPERADMIN_USERNAME
   - Password: $ALTA_TEST_SUPERADMIN_PASSWORD

2. **Moderator** - Limited permissions
   - Username: $ALTA_TEST_MODERATOR_USERNAME
   - Password: $ALTA_TEST_MODERATOR_PASSWORD

### Authentication

- Auth Endpoint: $ALTA_API_AUTH_ENDPOINT
- Method: POST with credentials

### Test Checklist

Based on the ticket requirements, the following areas will be tested:

#### Functional Tests
- [ ] Core functionality described in ticket
- [ ] Related features/workflows
- [ ] Data validation and error handling
- [ ] API integration points

#### Multi-Role Tests
- [ ] Superadmin role functionality
- [ ] Moderator role functionality
- [ ] Permission boundaries respected
- [ ] Role-specific UI elements

#### Regression Tests
- [ ] Previously working features unaffected
- [ ] No console errors introduced
- [ ] Performance not degraded

#### Edge Cases
- [ ] Empty/null input handling
- [ ] Boundary value testing
- [ ] Special character handling
- [ ] Network error scenarios

---

Proceeding with automated testing...
```

### 6. Execute UI Testing (if required)

If `NEEDS_UI_TEST=true`, delegate to the web-qa agent with comprehensive testing instructions.

**IMPORTANT**: You must delegate to the `web-qa` agent using the Task tool. Provide the agent with:

1. **Test Environment Details:**
   - Base URL: `$TEST_URL`
   - Environment: `$TEST_ENV`
   - Auth endpoint: `$ALTA_API_AUTH_ENDPOINT`

2. **Test Credentials:**
   - Superadmin: `$ALTA_TEST_SUPERADMIN_USERNAME` / `$ALTA_TEST_SUPERADMIN_PASSWORD`
   - Moderator: `$ALTA_TEST_MODERATOR_USERNAME` / `$ALTA_TEST_MODERATOR_PASSWORD`

3. **Test Requirements (from ticket):**
   - Subject: `$SUBJECT`
   - Description: `$DESCRIPTION`
   - Additional context from comments: `$JOURNALS`

4. **Testing Instructions:**
   - Test with BOTH roles (superadmin and moderator)
   - Follow the generated test checklist
   - Document all findings with severity levels
   - Capture screenshots of any issues (store in /tmp)
   - Check console for errors
   - Verify role-specific permissions

**Example Delegation Prompt:**

```
Please perform comprehensive QA testing for Redmine issue #$ISSUE_ID.

**Environment**: $TEST_ENV
**Base URL**: $TEST_URL
**Auth Endpoint**: $ALTA_API_AUTH_ENDPOINT

**Test Credentials**:

1. Superadmin Role:
   - Username: $ALTA_TEST_SUPERADMIN_USERNAME
   - Password: $ALTA_TEST_SUPERADMIN_PASSWORD

2. Moderator Role:
   - Username: $ALTA_TEST_MODERATOR_USERNAME
   - Password: $ALTA_TEST_MODERATOR_PASSWORD

**Issue Details**:

Subject: $SUBJECT

Description:
$DESCRIPTION

Additional Context:
$JOURNALS

**Testing Requirements**:

1. Test the functionality described in the issue with BOTH roles
2. Verify the following test checklist:
   - Core functionality works as expected
   - Form validation and error handling
   - Permission boundaries for each role
   - No console errors or network failures
   - Responsive design (if applicable)
   - Regression: existing features still work

3. For EACH role, document:
   - What works correctly
   - What fails or has issues
   - Permission-specific behaviors
   - Any unexpected behaviors

4. Capture screenshots of:
   - Successful flows
   - Any errors or issues found
   - Permission denied scenarios (if applicable)

5. Categorize findings by severity:
   - CRITICAL: Complete failure, data loss, security issue
   - HIGH: Major functionality broken
   - MEDIUM: Minor issues, cosmetic problems
   - LOW: Improvements/suggestions

Provide a detailed test report with your findings.
```

### 7. Process Test Results

After the web-qa agent completes testing, analyze the results and determine the QA status:

- **PASS**: All critical test cases pass, no blocking issues
- **FAIL**: Critical or high-severity issues found
- **BLOCKED**: Cannot complete testing due to environment/access issues

### 8. Format Results for Redmine

Transform the test results into the format required by `post-qa-comment`:

```bash
if [ "$NEEDS_UI_TEST" = true ]; then
  QA_STATUS="<PASS|FAIL|BLOCKED based on test results>"

  ISSUES_ARRAY="[]"

  BLOCKER=""

  cat <<EOF | "$REDMINE_TOOL" post-qa-comment -
{
  "issue_id": $ISSUE_ID,
  "status": "$QA_STATUS",
  "scope": "$SUBJECT",
  "environment": "$TEST_ENV"$([ "$QA_STATUS" = "FAIL" ] && echo ",
  \"issues\": $ISSUES_ARRAY")$([ "$QA_STATUS" = "BLOCKED" ] && [ -n "$BLOCKER" ] && echo ",
  \"blocker\": \"$BLOCKER\"")
}
EOF
else
  echo "No UI testing required for this ticket. Manual testing recommended."

  cat <<EOF | "$REDMINE_TOOL" post-qa-comment -
{
  "issue_id": $ISSUE_ID,
  "status": "PASS",
  "scope": "Automated analysis - no UI testing required",
  "environment": "$TEST_ENV"
}
EOF
fi
```

**Important**: When FAIL status is used, populate the `issues` array with findings from the web-qa agent:

```bash
ISSUES_ARRAY=$(cat <<'ISSUES_EOF'
[
  "Critical: Login fails for moderator role with 401 error",
  "High: Form validation missing for email field",
  "Medium: Button alignment issue on mobile viewport"
]
ISSUES_EOF
)
```

When BLOCKED status is used, set the blocker reason:

```bash
BLOCKER="Test environment is down - received 503 Service Unavailable"
```

### 9. Completion

After posting the QA comment:

1. Confirm the comment was posted successfully
2. Provide the Redmine issue URL for user reference
3. Summarize key findings

**Arguments**:

- Redmine issue URL (e.g., `/do-test https://redmine.int-tro.kz/issues/707`)

**Behavior**:

- Fetches complete ticket details including all comments
- Analyzes requirements to determine test scope and environment
- Generates comprehensive test checklist based on ticket content
- Invokes web-qa agent for UI testing with multiple roles (if applicable)
- Posts formatted QA results back to Redmine using post_qa_comment
- Supports role-based testing (superadmin, moderator)
- Automatically detects test environment (dev/staging/production)
- Stores screenshots in /tmp directory

**Test Role Credentials** (from ~/.secrets):

- Superadmin: `$ALTA_TEST_SUPERADMIN_USERNAME` / `$ALTA_TEST_SUPERADMIN_PASSWORD`
- Moderator: `$ALTA_TEST_MODERATOR_USERNAME` / `$ALTA_TEST_MODERATOR_PASSWORD`
- Auth Endpoint: `$ALTA_API_AUTH_ENDPOINT`

**Domain Mapping** (from ~/.secrets):

- Dev: `$ALTA_API_DEV_URL`
- Staging: `$ALTA_API_STAGE_URL`
- Production: `$ALTA_API_PROD_URL`

**Error Handling**:

- Invalid URL format
- Issue not found
- Network/API errors
- Environment unavailable
- Test failures
