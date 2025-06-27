from tests.process_flow_response import mock_response
from helpers.llm_to_flow_graph import convert_llm_steps_to_flow
import json

# Mock LLM structured response όπως μου έδωσες
mock_llm_response = {
    "flow": [
        {
            "step": "00000-MAIN",
            "action": "If EIBAID is equal to DFHPF3, perform XCTL to the program 'DOGEQUIT'.",
            "condition": "IF EIBAID EQUAL TO DFHPF3 THEN EXEC CICS XCTL PROGRAM('DOGEQUIT')"
        },
        {
            "step": "00000-MAIN",
            "action": "If WOW-MENU is true, move 'T' to DOGECOMMS-AREA and perform the action 'DOGE-MAIN-SCREEN'.",
            "condition": "IF WOW-MENU THEN MOVE 'T' TO DOGECOMMS-AREA PERFORM DOGE-MAIN-SCREEN"
        },
        {
            "step": "DOGE-MAIN-SCREEN",
            "action": "Start browsing the file 'DOGEVSAM' with RIDFLD(START-RECORD-ID).",
            "cics_command": "EXEC CICS STARTBR FILE('DOGEVSAM') RIDFLD(START-RECORD-ID)"
        },
        {
            "step": "DOGE-MAIN-SCREEN",
            "action": "Send a map with ID 'DOGEMN1' from the MAPSET 'DOGEMN' for erasing.",
            "cics_command": "EXEC CICS SEND MAP('DOGEMN1') MAPSET('DOGEMN') ERASE"
        }
    ]
}

# Κλήση του converter
filename = "workspace\\DOGECICS\\COBOL\\DOGEMAIN"
converted_graph = convert_llm_steps_to_flow(filename, mock_llm_response)

# Εμφάνιση αποτελέσματος
print(json.dumps(converted_graph, indent=2))
