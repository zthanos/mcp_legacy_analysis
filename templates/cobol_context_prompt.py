cobol_context_prompt = """
COBOL (Common Business-Oriented Language) is a procedural, structured language widely used in legacy enterprise systems such as banking, insurance, and government infrastructure.

A COBOL program consists of four main DIVISIONS:

1. **IDENTIFICATION DIVISION**: Contains metadata such as the program name.
2. **ENVIRONMENT DIVISION**: Describes input/output devices and runtime context.
3. **DATA DIVISION**: Declares variables, files, records, constants, and memory layouts.
4. **PROCEDURE DIVISION**: Contains the actual business logic and control flow.

---

### 💡 Key Syntax and Concepts:

#### 🧱 Program Structure:
- **SECTIONS** and **PARAGRAPHS** group logic hierarchically under PROCEDURE DIVISION.
- Each paragraph can be invoked via `PERFORM`.

#### 🔁 Control Flow:
- `PERFORM <paragraph>`: Simple invocation
- `PERFORM ... THROUGH ...`: Executes a block of paragraphs
- `PERFORM UNTIL <condition>`: Loop with condition
- `IF`, `EVALUATE`, `GO TO`: Decision making and branching

#### 📞 External Interactions:
- `CALL 'module-name' USING ...`: Calls to other programs or modules
- `EXEC SQL ... END-EXEC`: Embedded SQL for database interaction
- `EXEC TRU` / `EXEC CICS`: Transaction management (e.g., mainframe)

#### 📁 File Handling:
- Files defined using `FD`, `SELECT`, `ASSIGN TO`
- Operations: `OPEN INPUT/OUTPUT`, `READ`, `WRITE`, `CLOSE`

#### 📚 COPYBOOKS:
- `COPY name.`: Includes external structure (record layouts, constants)
- May reference external files needed to fully understand the program

#### 📦 Working Storage:
- Declared in `WORKING-STORAGE SECTION`
- Contains local variables, status flags, runtime data

#### 🔄 Memory Sharing (REDEFINES):
- `REDEFINES` allows overlapping storage, interpreting same data in different ways
- Useful for conditional parsing or multiple record types
- Example:
  ```cobol
  01 MY-RECORD.
     05 RAW-DATA        PIC X(10).
     05 NUMERIC-VIEW    REDEFINES RAW-DATA PIC 9(10).
"""