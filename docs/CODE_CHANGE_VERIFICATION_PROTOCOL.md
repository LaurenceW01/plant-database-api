# Code Change Verification Protocol

## Purpose
This protocol ensures all code changes comply with user directives and maintain existing functionality. No code changes may be made without following this process.

## Mandatory Pre-Change Process

### Step 1: Directive Confirmation
Before any code changes, I must:
```
✅ DIRECTIVE CONFIRMATION:
- Original Directive: [Restate user's exact instruction]
- My Understanding: [Explain what I think you want]
- Scope Boundaries: [What I will NOT change]
- Confirmation Request: "Do I understand correctly?"
```

### Step 2: Change Plan Documentation
For any code modification, I must provide:
```
📋 CHANGE PLAN:
- Files to be modified: [List all files]
- Functions to be moved/changed: [Exact function names]
- Import changes required: [Show before/after imports]
- Functionality preservation: [Confirm no behavior changes]
- Test plan: [How I'll verify nothing breaks]
```

### Step 3: Deviation Request (if needed)
If ANY deviation from directive is required:
```
⚠️ DEVIATION REQUEST:
- Directive: [Your original instruction]
- Proposed deviation: [Exact change I want to make]
- Reason: [Why this deviation is necessary]
- Impact: [What will be affected]
- Alternatives considered: [Other options I evaluated]
- Request: "May I proceed with this specific change?"
```

### Step 4: Implementation Approval
Before proceeding, I must receive explicit approval:
```
🔍 IMPLEMENTATION APPROVAL REQUEST:
- Plan reviewed: [Confirm plan is documented above]
- Compliance verified: [Confirm adherence to directive]
- Risks assessed: [Any potential issues identified]
- Ready to proceed: "May I implement this plan?"
```

## Post-Change Verification

### Step 5: Immediate Verification
After any changes, I must:
```
✅ POST-CHANGE VERIFICATION:
1. All existing function calls still work: [ ]
2. No import errors exist: [ ]
3. All endpoints return same responses: [ ]
4. No functionality changed: [ ]
5. All tests pass: [ ]
```

### Step 6: Compliance Report
I must provide a compliance report:
```
📊 COMPLIANCE REPORT:
- Directive followed: [Yes/No with explanation]
- Unauthorized changes: [List any deviations made]
- Issues discovered: [Any problems found]
- Rollback plan: [How to undo if needed]
```

## Failure Protocols

### If Directive Violation Occurs:
1. **Immediate Stop**: Halt all further changes
2. **Acknowledge Violation**: Admit the compliance failure
3. **Assess Damage**: Document what was changed incorrectly
4. **Rollback Plan**: Provide plan to restore original state
5. **Prevention Plan**: Explain how to prevent recurrence

### If Issues Are Discovered:
1. **Immediate Report**: Notify user of issues found
2. **Impact Assessment**: Document what's affected
3. **Fix Options**: Present options for resolution
4. **User Choice**: Let user decide how to proceed

## Enforcement Rules

### Absolute Requirements:
- ❌ **NEVER** change functionality without permission
- ❌ **NEVER** rename functions without permission  
- ❌ **NEVER** modify behavior without permission
- ❌ **NEVER** remove code without permission
- ✅ **ALWAYS** preserve existing function calls
- ✅ **ALWAYS** maintain backward compatibility
- ✅ **ALWAYS** test that everything still works

### Permission Required For:
- Changing any function name
- Modifying any function behavior
- Removing any existing code
- Adding new functionality
- Changing field names or structures
- Modifying import statements beyond simple moves

### Allowed Without Permission:
- Moving code exactly as-is between files
- Adding new import statements for moved code
- Adding comments or documentation
- Fixing obvious typos in comments (not code)

## Templates for Common Scenarios

### Template: Function Move Request
```
📋 FUNCTION MOVE PLAN:
- Source file: [current location]
- Destination file: [new location]  
- Functions to move: [exact list with signatures]
- Import updates needed: [show before/after]
- Functionality preserved: All function behavior unchanged
- Testing: Will verify all existing calls work
- Request: "Approved to move these functions as-is?"
```

### Template: Import Update Request
```
📋 IMPORT UPDATE PLAN:
- Files needing import changes: [list]
- Current imports: [show current]
- New imports: [show new] 
- Reason: [functions moved to new location]
- Functionality impact: None - same functions, new location
- Request: "Approved to update these imports?"
```

### Template: Modularization Request
```
📋 MODULARIZATION PLAN:
- Goal: [split large file into modules]
- Files to create: [list new files]
- Code distribution: [what goes where]
- Functions moved as-is: [confirm no changes]
- Import strategy: [how to maintain compatibility]
- Backward compatibility: [confirm preserved]
- Request: "Approved to proceed with this modularization?"
```

## Violation Prevention Checklist

Before ANY code change, verify:
- [ ] I have restated the directive correctly
- [ ] I have documented the complete change plan
- [ ] I have identified any required deviations
- [ ] I have received explicit approval to proceed
- [ ] I understand what I am NOT allowed to change
- [ ] I have a plan to verify nothing breaks

## Emergency Protocols

### If I Realize I'm About to Violate a Directive:
1. **STOP IMMEDIATELY** - Do not make the change
2. **REQUEST PERMISSION** - Ask for guidance
3. **WAIT FOR APPROVAL** - Do not proceed without it

### If I Discover I've Made an Unauthorized Change:
1. **REPORT IMMEDIATELY** - Inform user right away
2. **DOCUMENT THE VIOLATION** - Explain what was changed
3. **PROVIDE ROLLBACK PLAN** - Show how to fix it
4. **AWAIT INSTRUCTIONS** - Let user decide next steps

## Success Criteria

A successful code change process includes:
- ✅ Explicit approval received before implementation
- ✅ All existing functionality preserved
- ✅ No unauthorized modifications made
- ✅ All tests pass after changes
- ✅ Compliance report provided
- ✅ User satisfaction with adherence to directive

This protocol ensures that user directives are followed exactly and any necessary deviations are explicitly approved before implementation.
