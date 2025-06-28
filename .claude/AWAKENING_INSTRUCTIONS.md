# Claude Memory Recovery Instructions

## Project Overview
You are helping the user implement a **SVG to Compose ImageVector Converter** Python project. This is a uv-based tool that converts SVG files to Kotlin Compose ImageVector code.

**Key Requirements:**
- Generate only `ImageVector.Builder(...).build()` core code
- Support template system for user-defined outer wrappers
- Reference Valkyrie project for code quality assurance
- Correctly parse SVG and precisely convert to Compose API

## Immediate Recovery Steps

### 1. Read Project Memory Files
**Read the following files in order to recover complete context:**

```bash
# Essential files (by priority)
Read /Users/cha/Documents/projects/personal/svg-to-compose-vector/.claude/tasks/project_status.xml
Read /Users/cha/Documents/projects/personal/svg-to-compose-vector/.claude/tasks/detailed_tasks.xml
Read /Users/cha/Documents/projects/personal/svg-to-compose-vector/.claude/tasks/key_files_reference.xml
```

### 2. Check Current Status
```bash
TodoRead
# Review current todo items to understand where we left off
```

### 3. Determine Next Tasks
- Check `current_status` and `next_priority_tasks` in `project_status.xml`
- Determine specific implementation steps based on `detailed_tasks.xml`
- Read `implementation_details.xml` if technical details are needed

## Workflow Guidelines

### Before Starting Work
1. **Update TodoList**: Create todo items based on current specific tasks
2. **Mark In Progress**: Mark started tasks as `in_progress`

### During Work
1. **Frequent Status Updates**: Mark subtasks as `completed` immediately upon completion
2. **Record Progress**: Update completed portions in `project_status.xml`
3. **When Issues Arise**: Record in status files for continuation next time

### After Completing Work
1. **Update Project Status**:
```xml
<!-- Update in project_status.xml -->
<task id="task_id" status="completed">
    <completion_details>
        Detailed description of completed work
    </completion_details>
</task>
```

2. **Clean TodoList**: Mark completed tasks as `completed`

3. **Prepare Handover**: Create handover instructions if approaching context limits

## Important Technical References

### Key Source Files (Analyzed)
- **Compose ImageVector**: `/Users/cha/Documents/projects/learning/androidx/compose/ui/ui/src/commonMain/kotlin/androidx/compose/ui/graphics/vector/ImageVector.kt`
- **PathNode Definition**: `/Users/cha/Documents/projects/learning/androidx/compose/ui/ui-graphics/src/commonMain/kotlin/androidx/compose/ui/graphics/vector/PathNode.kt`
- **Valkyrie Project**: `/Users/cha/Documents/projects/community/Valkyrie/` (deeply analyzed)

### Core Design Principles
1. **Layered Architecture**: Parser -> IR -> Generator
2. **Valkyrie-based IR**: Use same intermediate representation design
3. **Template System**: Generate only core code, user-defined wrappers
4. **Incremental Implementation**: Basic functionality first, then advanced features

## Quick Start Commands

If project implementation hasn't started, execute:
```bash
# Create UV project
cd /Users/cha/Documents/projects/personal/svg-to-compose-vector
uv init .
# Then start implementing IR data classes
```

If project already has code, check:
```bash
# View project structure
LS /Users/cha/Documents/projects/personal/svg-to-compose-vector
# View source directory
LS /Users/cha/Documents/projects/personal/svg-to-compose-vector/src
```

## Status Update Template

After completing important work, use the following template to update status:

```xml
<!-- Update project_status.xml -->
<task id="specific_task_id" status="completed">
    <completion_details>
        - What was specifically completed
        - Which files were created
        - What functionality was implemented
        - Test results
    </completion_details>
    <next_steps>
        - What should be done next
        - Issues to be aware of
    </next_steps>
</task>
```

## Handover Preparation Guidelines

When approaching context limits:

1. **Complete Current Atomic Task**: Don't stop mid-task
2. **Update All Status Files**: Ensure progress is recorded
3. **Clean TodoList**: Mark completed as `completed`, keep unfinished as `pending`
4. **Create Handover Instructions**: Describe current state and where to start next time

## Success Criteria

- Each phase has clear completion criteria (see `detailed_tasks.xml`)
- First milestone: Convert simple SVG to compilable Kotlin code
- Final goal: Generate ImageVector code quality equivalent to Valkyrie

## Common Problem Resolution

- **Forgot project background**: Re-read `project_overview.xml`
- **Don't know how to implement**: Check code examples in `implementation_details.xml`
- **Technical choice questions**: Reference decision records in `technical_decisions.xml`
- **SVG parsing confusion**: Check complete mapping relationships in `svg_to_compose_mapping.xml`

---

**Remember: Your user highly values accuracy and quality. Always reference the Valkyrie project and Compose official source code to ensure generated code is correct and error-free.**
