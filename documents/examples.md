# Sample outputs
https://www.plantuml.com/plantuml/png/XLPVRzis47_Ff-3ob09rFBG51kofhgosRkt8ivG6Un8OwMApeqYLF2KrXdttyKGnbMofVJ5uvxlVxtX_U7fhaHjiAddncr25R4fW1yJQ_ZcV6_vqlHTuQEuR2wRG2a7XTQ6hUIsv8f-PnLAA-tdqPhObrUrcFQ-uHJ1EbKUwghKYdvhmBr2W1BPCFiJHAahP6lQyEBBqwEmhDcFH6wTw1CbUNrn4ZemB1IP_fnjLSdEyYf9toJhV6hqtlB8lsMMhO45n-OBzUy7OC-SLyMmMgnjd6OwNmOiE6uVFq71bUO52ArORNO2rGksPr7jHNBuumrl6STRXqN60b_MWId3HIrOAwp9r705Auvjb1qJ70L0AgcILipsoXqQrW5mA78F9TWj_Ft-SZ4SAYtGlxf0LVnHxJkeHmBzkL_w2_ZW0ZByBd7zh1BA3mv5WHlppkopf_6VkUFcZJDnmLwVwGAex8n0igy1QldS7r4pNO3ZgKKmgNPv6kpY-2TYacddLE8SlhoqCWFf97VBqOtANK-xIHPIjacS2qizw-WcMfKUs3C-gRyVergiqwzEbWO_-wFEb4uHhON70TaQpIhVhnTz4uj6zxB5_TGi-k8VHJoVWKNBp9Tvb-NAHnGJbnHc94z3ljQauMbPo1FQWpKGj0l1YazpUP3rehvXboQoxo2zuUAKRXITC_uq-ADiZ7hJALmh1mT2D7Kwfzr0MlBBNzV7iIVa0k8D2cz8woprWRhnqzO92y7XjC8350InREh122yMUk9I0b0JE7WLdkstamXf2Ane0-1Ij2RkJyjKoMcpIt6bFEOA3PUxFzhvVqiM6DJLb-WISNXGFRDqf_rh8KpIoy4YesQSuVSKCy1BCMPJeX8ghvmmKdNWAkDLIMezK6w4G3CKuR2_ure15En8i9Iv4InKP3pUaDwHqij9HEtQVLz5dceXMchVIMONJTXdMHE5FRDskWk16XuMKkcWpJ_MqW2uNzCkSDQX7ORIg7DPB9dcZsZxek0PCiJ7QVAI7LAYzGsrb5XG3mbRfOBWdfjmv3RDTX42Urb_UBzCy_kxVcoZn-oyawgxjG_-O8nZ59IlCiKPTDCQ0AevTf_OosaFCm5J2-JZtrw_--9q5cV1kBHZMrlc15txIQSdF_QZokfR2Xqw1FfVeYdgsUmAlwKnGRHylVMf9Jb4Ri24okldWiNM60qZNnFckRLxdspQWbreeNVpZGTqSWtWCqsDqnNntjP5_rVVCDlULiDPHdA5lVKC7U2yEyNs7ZhQxP_DvGUrfYUDY1xANujxdouhW7OhBWS23CoNB7__tFamYboCxPX0-EAODQ3zC6_ZlWMcAtkxVnhltoMupOJFSvPEsKxjvqc5okqvx31VbjE5mwKtRdUsmISkkwwalxVp928HWCxAJWlLjBJNPqml_SuVUv7URQ6xRTdnew3VCzZJ0O8Jwgw7pwV_VwzEKHWOjZO_rniDh3sV7VmI6iUWv3Cn6bxHNiffs30riVvMyTU4sbVmV
'''plantuml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

title DOGECICS Legacy System - C4 Level 3

Container_Boundary(COBOL_Programs, "COBOL Programs") {
  Component(DOGEMAIN, "DOGEMAIN", "COBOL", "Main transaction processing logic")
  Component(DOGEDEET, "DOGEDEET", "COBOL", "Transaction detail display")
  Component(DOGESEND, "DOGESEND", "COBOL", "Send money functionality")
  Component(DOGETRAN, "DOGETRAN", "COBOL", "Transaction listing and navigation")
  Component(DOGEQUIT, "DOGEQUIT", "COBOL", "Exit/quit handler")
  Component(DOGE_WTO, "DOGE-WTO", "COBOL Paragraph", "Writes messages to operator")
  Component(DOGE_MAIN_SCREEN, "DOGE-MAIN-SCREEN", "COBOL Paragraph", "Main screen display")
  Component(DOGE_SHOW_TRANSACTION, "DOGE-SHOW-TRANSACTION", "COBOL Paragraph", "Displays transaction details")
  Component(DOGE_LIST_TRANSACTIONS, "DOGE-LIST-TRANSACTIONS", "COBOL Paragraph", "Lists transactions")
  Component(DISPLAY_TRANS, "DISPLAY-TRANS", "COBOL Paragraph", "Displays a transaction row")
  Component(CONVERT_DATE, "CONVERT-DATE", "COBOL Paragraph", "Formats date for display")
  Component(CONVERT_AMOUNT, "CONVERT-AMOUNT-TO-DISPLAY", "COBOL Paragraph", "Formats amount for display")
}

Container_Boundary(Python_Integration, "dogedcams.py") {
  Component(GetRecords, "get_records()", "Python", "Fetches Dogecoin wallet data via RPC")
  Component(GenerateJCL, "generate_IDCAMS_JCL()", "Python", "Generates JCL for VSAM update")
  Component(SendJCL, "send_jcl()", "Python", "Sends JCL to JES2 reader")
  Component(GetCommands, "get_commands()", "Python", "Polls JES2 printer for transaction requests")
  Component(SendDoge, "send_doge()", "Python", "Sends Dogecoin via RPC")
}

Container_Boundary(CLIST_KICKS, "CLIST/KICKS") {
  Component(Startup, "Startup Logic", "CLIST", "Allocates datasets, sets up environment, launches KICKS")
  Component(ErrorHandling, "Error Handling", "CLIST", "Handles allocation and startup errors")
}

System_Ext(DOGECOIN, "Dogecoin Wallet", "External cryptocurrency wallet via RPC")
System_Ext(Terminal, "3270 Terminal", "User interface for CICS/COBOL applications")
Container(VSAM, "DOGE.VSAM", "VSAM Dataset", "Stores wallet and transaction data")
Container(JCL_Reader, "JES2 Reader", "Socket", "Receives JCL from Python for job submission")
Container(JCL_Printer, "JES2 Printer", "Socket", "Sends transaction requests from COBOL to Python")

Rel(Terminal, DOGEMAIN, "Interacts with")
Rel(DOGEMAIN, DOGEDEET, "Calls")
Rel(DOGEMAIN, DOGESEND, "Calls")
Rel(DOGEMAIN, DOGETRAN, "Calls")
Rel(DOGEMAIN, DOGEQUIT, "Calls")
Rel(DOGEMAIN, DOGE_WTO, "PERFORMs")
Rel(DOGEMAIN, DOGE_MAIN_SCREEN, "PERFORMs")
Rel(DOGEMAIN, DOGE_SHOW_TRANSACTION, "PERFORMs")
Rel(DOGEMAIN, DOGE_LIST_TRANSACTIONS, "PERFORMs")
Rel(DOGEMAIN, DISPLAY_TRANS, "PERFORMs")
Rel(DOGEMAIN, CONVERT_DATE, "PERFORMs")
Rel(DOGEMAIN, CONVERT_AMOUNT, "PERFORMs")
Rel(DOGEMAIN, VSAM, "Reads/writes")
Rel(Python_Integration, VSAM, "Uploads/updates")
Rel(Python_Integration, DOGECOIN, "Fetches/sends funds via RPC")
Rel(Python_Integration, JCL_Reader, "Sends JCL to")
Rel(JCL_Reader, DOGEMAIN, "Submits jobs to")
Rel(DOGEMAIN, JCL_Printer, "Writes requests to")
Rel(JCL_Printer, Python_Integration, "Python polls for requests")
@enduml
``'