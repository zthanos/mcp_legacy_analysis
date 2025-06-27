mock_response = {
    "filename": "workspace\\DOGECICS\\COBOL\\DOGEMAIN",
    "flow_graph": [
        {
            "node": "00000-MAIN",
            "type": "paragraph",
            "is_entry_point": True,
            "edges_to": [
                {"target": "DOGE-MAIN-SCREEN", "transfer_type": "PERFORM", "integration_type": "internal"},
                {"target": "DOGEQUIT", "transfer_type": "CALL", "integration_type": "external"},
                {"target": "DOGECOIN", "transfer_type": "CALL", "integration_type": "external"},
                {"target": "DOGESEND", "transfer_type": "CALL", "integration_type": "external"},
            ]
        },
        {
            "node": "DOGE-MAIN-SCREEN",
            "type": "paragraph",
            "is_entry_point": False,
            "edges_to": [
                {"target": "CONVERT-DATE", "transfer_type": "PERFORM", "integration_type": "internal"},
                {"target": "CONVERT-AMOUNT-TO-DISPLAY", "transfer_type": "PERFORM", "integration_type": "internal"},
                {"target": "DOGEMN1", "transfer_type": "EXEC CICS SEND MAP", "integration_type": "external"},
            ]
        }
    ]
}


complex_mock = {
    "flow": [
        {
            "step": "DOGE-MAIN-SCREEN",
            "action": "Convert the date and move it to DDATE.",
            "sub_steps": [
                {
                    "step": "CONVERT-DATE",
                    "cics_command": "EXEC CICS FORMATTIME ABSTIME(TEMP-DATE) DATESEP('/') MMDDYYYY(DDATE)"
                }
            ]
        },
        {
            "step": "DOGE-MAIN-SCREEN",
            "action": "Convert the amount to display format and move it to DAMOUNT.",
            "sub_steps": [
                {
                    "step": "CONVERT-AMOUNT-TO-DISPLAY",
                    "actions": [
                        {
                            "action": "Move DFHGREEN to RECENT-COLOR.",
                            "cics_command": "MOVE DFHGREEN TO RECENT-COLOR"
                        },
                        {
                            "action": "Convert the number from VSAM to ##,###,###.######## and move it to DAMOUNT.",
                            "condition": "IF TAMT-SIGN-NEGATIVE THEN MOVE DFHRED TO RECENT-COLOR SUBTRACT THE-AMOUNT FROM ZERO GIVING THE-AMOUNT MOVE THE-AMOUNT TO DAMOUNT"
                        }
                    ]
                }
            ]
        }
    ]
}
