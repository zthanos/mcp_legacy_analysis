import hashlib

def process_execution_flow(filename, llm_data):
    nodes = {}
    seen_edges = set()  # Αποφυγή διπλότυπων edges

    def generate_unique_name(base, content):
        hash_digest = hashlib.md5(content.encode()).hexdigest()[:6]
        return f"{base}-{hash_digest}"

    def process_step(step, parent=None):
        step_name = step["step"]

        if step_name not in nodes:
            nodes[step_name] = {
                "node": step_name,
                "type": "paragraph",
                "is_entry_point": step_name == "00000-MAIN",
                "edges_to": []
            }

        targets = []
        cmd = step.get("cics_command", "") + " " + step.get("action", "") + " " + step.get("condition", "")

        # Patterns για επέκταση
        patterns = [
            {"keyword": "EXEC SQL", "transfer_type": "SQL EXECUTION", "integration_type": "external", "target": "DATABASE"},
            {"keyword": "HTTP GET", "transfer_type": "API CALL", "integration_type": "external", "target": "UNKNOWN-API"},
            {"keyword": "HTTP POST", "transfer_type": "API CALL", "integration_type": "external", "target": "UNKNOWN-API"},
            {"keyword": "curl", "transfer_type": "API CALL", "integration_type": "external", "target": "UNKNOWN-API"},
            {"keyword": "WRITE FILE(", "transfer_type": "FILE WRITE", "integration_type": "external", "extract_func": "extract_text", "extract_args": ("WRITE FILE('", "')")},
            {"keyword": "SPOOLWRITE", "transfer_type": "FILE WRITE", "integration_type": "external", "target": "SPOOL"}
        ]

        # Εφαρμογή patterns
        for rule in patterns:
            if rule["keyword"] in cmd:
                extracted_target = rule.get("target", "UNKNOWN-TARGET")
                if "extract_func" in rule:
                    extracted_target = extract_text(cmd, *rule["extract_args"])
                targets.append(edge(extracted_target, rule["transfer_type"], rule["integration_type"]))

        # Παλιότερες εξειδικευμένες λογικές (αν θες να τις κρατήσεις)
        if "FORMATTIME" in cmd:
            targets.append(edge("DDATE", "TIME FORMAT", "external"))
        if "XCTL PROGRAM(" in cmd:
            prog = extract_text(cmd, "PROGRAM('", "')")
            targets.append(edge(prog, "CALL", "external"))
        if "SEND MAP(" in cmd:
            targets.append(edge("MAP_DISPLAY", "EXEC CICS SEND", "external"))
        if "READNEXT FILE(" in cmd or "READPREV FILE(" in cmd:
            file_target = extract_text(cmd, "FILE('", "')")
            targets.append(edge(file_target, "FILE READ", "external"))
        if "RETURN TRANSID(" in cmd:
            targets.append(edge("TRANSACTION_RETURN", "RETURN", "external"))

        # Conditions
        cond = step.get("condition", "")
        if "PERFORM" in cond:
            perf_target = extract_perform_target(cond)
            if perf_target:
                targets.append(edge(perf_target, "PERFORM", "internal"))
        if "CALL" in cond:
            called_prog = extract_call_target(cond)
            if called_prog:
                targets.append(edge(called_prog, "CALL", "external"))

        # Καταχώρηση μοναδικών edges
        for tgt in targets:
            edge_key = (step_name, tgt["target"], tgt["transfer_type"])
            if edge_key not in seen_edges:
                nodes[step_name]["edges_to"].append(tgt)
                seen_edges.add(edge_key)

        # Nested sub-steps και actions
        if "sub_steps" in step:
            for sub in step["sub_steps"]:
                sub_name = generate_unique_name(sub["step"], sub.get("action", "") + sub.get("cics_command", ""))
                sub["step"] = sub_name
                process_step(sub, parent=step_name)
        if "actions" in step:
            for act in step["actions"]:
                act_name = generate_unique_name(step_name + "-ACT", act.get("action", "") + act.get("cics_command", ""))
                act["step"] = act_name
                process_step(act, parent=step_name)

        if parent:
            edge_key = (parent, step_name, "PERFORM")
            if edge_key not in seen_edges:
                nodes[parent]["edges_to"].append(edge(step_name, "PERFORM", "internal"))
                seen_edges.add(edge_key)

    # Επεξεργασία όλων των αρχικών βημάτων
    for top_step in llm_data.get("flow", []):
        process_step(top_step)

    return {"filename": filename, "flow_graph": list(nodes.values())}


# ----------------- Βοηθητικές -----------------

def extract_text(text, prefix, suffix):
    start = text.find(prefix) + len(prefix)
    end = text.find(suffix, start)
    return text[start:end] if start > len(prefix) - 1 and end > start else "UNKNOWN-TARGET"

def extract_perform_target(condition):
    tokens = condition.split()
    for i, token in enumerate(tokens):
        if token == "PERFORM" and i + 1 < len(tokens):
            return tokens[i + 1]
    return None

def extract_call_target(condition):
    tokens = condition.split()
    for i, token in enumerate(tokens):
        if token == "CALL" and i + 1 < len(tokens):
            return tokens[i + 1].strip("'\"")
    return None

def edge(target, transfer_type, integration_type):
    return {"target": target, "transfer_type": transfer_type, "integration_type": integration_type}
