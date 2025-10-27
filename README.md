# Bedrock_AstraDB 
Bedrock Agent + AstraDB RAG integration

**Purpose:** Connect an Amazon Bedrock Agent (named `youtubeAgentShra`) to DataStax AstraDB to enable Retrieval-Augmented Generation (RAG). This repo contains:

* `Lambda_Function.py` — AWS Lambda handler that the agent calls to run semantic vector searches against AstraDB.
* `AgentSpecification.md` — Human-readable agent spec describing behavior, action groups, and expected inputs/outputs.
* `jayfly_wikipedia.pdf` — A ~1000-word fictional Wikipedia-style article about the JayFly (for ingestion into AstraDB).
* `ScreenShot of Outputs.md` —Add output screenshot to documention.
