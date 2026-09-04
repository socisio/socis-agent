---
sidebar_position: 9
title: "Optional Skills Catalog"
description: "Official optional skills shipped with socis-agent — install via socis skills install official/<category>/<skill>"
---

# Optional Skills Catalog

Optional skills ship with socis-agent under `optional-skills/` but are **not active by default**. Install them explicitly:

```bash
socis skills install official/<category>/<skill>
```

For example:

```bash
socis skills install official/blockchain/solana
socis skills install official/mlops/flash-attention
```

Each skill below links to a dedicated page with its full definition, setup, and usage.

To uninstall:

```bash
socis skills uninstall <skill-name>
```

## autonomous-ai-agents

| Skill | Description |
|-------|-------------|
| [**agent-merge-conflict-arbiter**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-agent-merge-conflict-arbiter) | Neutral arbiter for merge conflicts between two agents. |
| [**antigravity-cli**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-antigravity-cli) | Operate the Antigravity CLI (agy): plugins, auth, sandbox. |
| [**blackbox**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-blackbox) | Delegate coding tasks to the Blackbox AI multi-model CLI. |
| [**grok**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-grok) | Delegate coding to xAI Grok Build CLI (features, PRs). |
| [**honcho**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-honcho) | Configure and troubleshoot Honcho memory for SOCIS. |
| [**openhands**](/docs/user-guide/skills/optional/autonomous-ai-agents/autonomous-ai-agents-openhands) | Delegate coding to OpenHands CLI (model-agnostic, LiteLLM). |

## blockchain

| Skill | Description |
|-------|-------------|
| [**evm**](/docs/user-guide/skills/optional/blockchain/blockchain-evm) | Read-only EVM client: wallets, tokens, gas across 8 chains. |
| [**hyperliquid**](/docs/user-guide/skills/optional/blockchain/blockchain-hyperliquid) | Hyperliquid market data, account history, trade review. |
| [**solana**](/docs/user-guide/skills/optional/blockchain/blockchain-solana) | Query Solana wallets, tokens, txs, and NFTs in USD. |

## communication

| Skill | Description |
|-------|-------------|
| [**one-three-one-rule**](/docs/user-guide/skills/optional/communication/communication-one-three-one-rule) | 1-3-1 decision briefs: problem, three options, one pick. |

## creative

| Skill | Description |
|-------|-------------|
| [**ascii-art**](/docs/user-guide/skills/optional/creative/creative-ascii-art) | ASCII art: pyfiglet, cowsay, boxes, image-to-ascii. |
| [**audiocraft-audio-generation**](/docs/user-guide/skills/optional/creative/creative-audiocraft-audio-generation) | AudioCraft: MusicGen text-to-music, AudioGen text-to-sound. |
| [**baoyu-article-illustrator**](/docs/user-guide/skills/optional/creative/creative-baoyu-article-illustrator) | Article illustrations: type × style × palette consistency. |
| [**baoyu-comic**](/docs/user-guide/skills/optional/creative/creative-baoyu-comic) | Knowledge comics (知识漫画): educational, biography, tutorial. |
| [**comfyui**](/docs/user-guide/skills/optional/creative/creative-comfyui) | Generate images, video, and audio via diffusion workflows. |
| [**concept-diagrams**](/docs/user-guide/skills/optional/creative/creative-concept-diagrams) | Generate flat, minimal educational SVG visuals as HTML. |
| [**creative-ideation**](/docs/user-guide/skills/optional/creative/creative-creative-ideation) | Generate ideas via named methods from creative practice. |
| [**draw-your-font**](/docs/user-guide/skills/optional/creative/creative-draw-your-font) | Turn a handwriting photo into an installable TTF font. |
| [**excalidraw**](/docs/user-guide/skills/optional/creative/creative-excalidraw) | Hand-drawn Excalidraw JSON diagrams (arch, flow, seq). |
| [**heartmula**](/docs/user-guide/skills/optional/creative/creative-heartmula) | HeartMuLa: Suno-like song generation from lyrics + tags. |
| [**hyperframes**](/docs/user-guide/skills/optional/creative/creative-hyperframes) | Render MP4/WebM videos from HTML compositions. |
| [**impeccable**](/docs/user-guide/skills/optional/creative/creative-impeccable) | Frontend design guidance, upstream-maintained (impeccable). |
| [**kanban-video-orchestrator**](/docs/user-guide/skills/optional/creative/creative-kanban-video-orchestrator) | Plan and run multi-agent video production pipelines. |
| [**meme-generation**](/docs/user-guide/skills/optional/creative/creative-meme-generation) | Create meme PNGs from templates with Pillow text overlay. |
| [**pixel-art**](/docs/user-guide/skills/optional/creative/creative-pixel-art) | Pixel art w/ era palettes (NES, Game Boy, PICO-8). |
| [**pretext**](/docs/user-guide/skills/optional/creative/creative-pretext) | Build creative browser demos with DOM-free text layout. |
| [**simple-english**](/docs/user-guide/skills/optional/creative/creative-simple-english) | Rewrite text to ASD-STE100 Simplified Technical English. |
| [**sketch**](/docs/user-guide/skills/optional/creative/creative-sketch) | Throwaway HTML mockups: 2-3 design variants to compare. |
| [**social-media-content-calendar**](/docs/user-guide/skills/optional/creative/creative-social-media-content-calendar) | Plan multi-platform social campaigns: briefs to posting. |
| [**tldraw-offline**](/docs/user-guide/skills/optional/creative/creative-tldraw-offline) | Drive and script tldraw offline canvases with an agent. |
| [**touchdesigner-mcp**](/docs/user-guide/skills/optional/creative/creative-touchdesigner-mcp) | Control TouchDesigner via twozero MCP. |
| [**unreal-mcp**](/docs/user-guide/skills/optional/creative/creative-unreal-mcp) | Automate Unreal Engine editor scenes, actors, and renders. |

## data-science

| Skill | Description |
|-------|-------------|
| [**jupyter-notebook**](/docs/user-guide/skills/optional/data-science/data-science-jupyter-notebook) | Iterative Python via live Jupyter kernel (hamelnb). |

## devops

| Skill | Description |
|-------|-------------|
| [**actual-setup**](/docs/user-guide/skills/optional/devops/devops-actual-setup) | Set up Actual Computer (actual.inc) inference in SOCIS. |
| [**docker-management**](/docs/user-guide/skills/optional/devops/devops-docker-management) | Manage Docker containers, images, volumes, and Compose. |
| [**inference-sh-cli**](/docs/user-guide/skills/optional/devops/devops-inference-sh-cli) | Run 150+ AI apps (image, video, LLM) via inference.sh CLI. |
| [**pinggy-tunnel**](/docs/user-guide/skills/optional/devops/devops-pinggy-tunnel) | Zero-install localhost tunnels over SSH via Pinggy. |
| [**setup-wizard-generator**](/docs/user-guide/skills/optional/devops/devops-setup-wizard-generator) | Generate a bash wizard guiding a human through manual setup. |
| [**socis-s6-container-supervision**](/docs/user-guide/skills/optional/devops/devops-socis-s6-container-supervision) | Modify or debug s6 services in the SOCIS Docker image. |
| [**watchers**](/docs/user-guide/skills/optional/devops/devops-watchers) | Poll RSS, JSON APIs, and GitHub with watermark dedup. |

## dogfood

| Skill | Description |
|-------|-------------|
| [**adversarial-ux-test**](/docs/user-guide/skills/optional/dogfood/dogfood-adversarial-ux-test) | Roleplay a hostile user to find and triage UX pain points. |

## email

| Skill | Description |
|-------|-------------|
| [**agentmail**](/docs/user-guide/skills/optional/email/email-agentmail) | Use when an agent needs AgentMail CLI email inboxes. |

## finance

| Skill | Description |
|-------|-------------|
| [**3-statement-model**](/docs/user-guide/skills/optional/finance/finance-3-statement-model) | Build integrated IS/BS/CF financial workbooks in Excel. |
| [**comps-analysis**](/docs/user-guide/skills/optional/finance/finance-comps-analysis) | Build comparable-company valuation workbooks in Excel. |
| [**dcf-model**](/docs/user-guide/skills/optional/finance/finance-dcf-model) | Build discounted cash flow valuation workbooks in Excel. |
| [**excel-author**](/docs/user-guide/skills/optional/finance/finance-excel-author) | Build auditable financial workbooks headless via openpyxl. |
| [**lbo-model**](/docs/user-guide/skills/optional/finance/finance-lbo-model) | Build leveraged buyout workbooks with IRR/MOIC in Excel. |
| [**merger-model**](/docs/user-guide/skills/optional/finance/finance-merger-model) | Build M&A accretion/dilution workbooks in Excel. |
| [**polymarket**](/docs/user-guide/skills/optional/finance/finance-polymarket) | Query Polymarket: markets, prices, orderbooks, history. |
| [**pptx-author**](/docs/user-guide/skills/optional/finance/finance-pptx-author) | Build PowerPoint decks headless with python-pptx. |
| [**stocks**](/docs/user-guide/skills/optional/finance/finance-stocks) | Stock quotes, history, search, compare, crypto via Yahoo. |

## gaming

| Skill | Description |
|-------|-------------|
| [**minecraft-modpack-server**](/docs/user-guide/skills/optional/gaming/gaming-minecraft-modpack-server) | Host modded Minecraft servers (CurseForge, Modrinth). |
| [**pokemon-player**](/docs/user-guide/skills/optional/gaming/gaming-pokemon-player) | Play Pokemon via headless emulator + RAM reads. |

## health

| Skill | Description |
|-------|-------------|
| [**fitness-nutrition**](/docs/user-guide/skills/optional/health/health-fitness-nutrition) | Workout planning, macros, and body metrics via wger/USDA. |
| [**neuroskill-bci**](/docs/user-guide/skills/optional/health/health-neuroskill-bci) | Use live BCI cognitive and mood state from NeuroSkill. |

## mcp

| Skill | Description |
|-------|-------------|
| [**fastmcp**](/docs/user-guide/skills/optional/mcp/mcp-fastmcp) | Build, test, and deploy Python MCP servers. |
| [**mcp-oauth-remote-gateway**](/docs/user-guide/skills/optional/mcp/mcp-mcp-oauth-remote-gateway) | Manual OAuth for remote MCP servers on headless gateways. |
| [**mcporter**](/docs/user-guide/skills/optional/mcp/mcp-mcporter) | List, auth, and call MCP servers/tools from the terminal. |

## migration

| Skill | Description |
|-------|-------------|
| [**openclaw-migration**](/docs/user-guide/skills/optional/migration/migration-openclaw-migration) | Import an OpenClaw setup (memories, skills) into SOCIS. |

## mlops

| Skill | Description |
|-------|-------------|
| [**accelerate**](/docs/user-guide/skills/optional/mlops/mlops-accelerate) | Run PyTorch training across GPUs with minimal changes. |
| [**axolotl**](/docs/user-guide/skills/optional/mlops/mlops-training-axolotl) | Axolotl: YAML LLM fine-tuning (LoRA, DPO, GRPO). |
| [**chroma**](/docs/user-guide/skills/optional/mlops/mlops-chroma) | Embedding database for RAG and semantic search. |
| [**clip**](/docs/user-guide/skills/optional/mlops/mlops-clip) | Zero-shot image classification and image-text search. |
| [**dspy**](/docs/user-guide/skills/optional/mlops/mlops-research-dspy) | DSPy: declarative LM programs, auto-optimize prompts, RAG. |
| [**evaluating-llms-harness**](/docs/user-guide/skills/optional/mlops/mlops-evaluation-evaluating-llms-harness) | lm-eval-harness: benchmark LLMs (MMLU, GSM8K, etc.). |
| [**faiss**](/docs/user-guide/skills/optional/mlops/mlops-faiss) | Fast vector similarity search at billion scale. |
| [**flash-attention**](/docs/user-guide/skills/optional/mlops/mlops-flash-attention) | Speed up long-sequence transformer training and inference. |
| [**guidance**](/docs/user-guide/skills/optional/mlops/mlops-guidance) | Constrain LLM output with grammars; guarantee valid JSON. |
| [**huggingface-hub**](/docs/user-guide/skills/optional/mlops/mlops-models-huggingface-hub) | HuggingFace hf CLI: search/download/upload models, datasets. |
| [**huggingface-tokenizers**](/docs/user-guide/skills/optional/mlops/mlops-huggingface-tokenizers) | Fast BPE/WordPiece tokenization and custom vocab training. |
| [**instructor**](/docs/user-guide/skills/optional/mlops/mlops-instructor) | Structured LLM outputs validated with Pydantic. |
| [**lambda-labs**](/docs/user-guide/skills/optional/mlops/mlops-lambda-labs) | On-demand GPU cloud instances for ML training. |
| [**llama-cpp**](/docs/user-guide/skills/optional/mlops/mlops-inference-llama-cpp) | llama.cpp local GGUF inference + HF Hub model discovery. |
| [**llava**](/docs/user-guide/skills/optional/mlops/mlops-llava) | Vision-language chat: VQA, captioning, image dialogue. |
| [**modal**](/docs/user-guide/skills/optional/mlops/mlops-modal) | Serverless GPU cloud for ML jobs and model APIs. |
| [**nemo-curator**](/docs/user-guide/skills/optional/mlops/mlops-nemo-curator) | Curate LLM training data: dedupe, filter, PII redaction. |
| [**obliteratus**](/docs/user-guide/skills/optional/mlops/mlops-obliteratus) | OBLITERATUS: abliterate LLM refusals (diff-in-means). |
| [**outlines**](/docs/user-guide/skills/optional/mlops/mlops-inference-outlines) | Outlines: structured JSON/regex/Pydantic LLM generation. |
| [**peft**](/docs/user-guide/skills/optional/mlops/mlops-peft) | Fine-tune large LLMs with LoRA on limited GPU memory. |
| [**pinecone**](/docs/user-guide/skills/optional/mlops/mlops-pinecone) | Managed vector DB for production RAG and search. |
| [**pytorch-fsdp**](/docs/user-guide/skills/optional/mlops/mlops-pytorch-fsdp) | Fully sharded data-parallel training for large models. |
| [**pytorch-lightning**](/docs/user-guide/skills/optional/mlops/mlops-pytorch-lightning) | Clean training loops with built-in distributed support. |
| [**qdrant**](/docs/user-guide/skills/optional/mlops/mlops-qdrant) | Vector search engine for production RAG systems. |
| [**saelens**](/docs/user-guide/skills/optional/mlops/mlops-saelens) | Train sparse autoencoders to interpret model features. |
| [**segment-anything-model**](/docs/user-guide/skills/optional/mlops/mlops-models-segment-anything-model) | SAM: zero-shot image segmentation via points, boxes, masks. |
| [**serving-llms-vllm**](/docs/user-guide/skills/optional/mlops/mlops-inference-serving-llms-vllm) | vLLM: high-throughput LLM serving, OpenAI API, quantization. |
| [**simpo**](/docs/user-guide/skills/optional/mlops/mlops-simpo) | Reference-free preference alignment, simpler than DPO. |
| [**slime**](/docs/user-guide/skills/optional/mlops/mlops-slime) | RL post-training for LLMs with Megatron and SGLang. |
| [**stable-diffusion**](/docs/user-guide/skills/optional/mlops/mlops-stable-diffusion) | Text-to-image generation, inpainting, and img2img. |
| [**tensorrt-llm**](/docs/user-guide/skills/optional/mlops/mlops-tensorrt-llm) | High-throughput LLM inference on NVIDIA GPUs. |
| [**torchtitan**](/docs/user-guide/skills/optional/mlops/mlops-torchtitan) | Pretrain LLMs at scale with PyTorch 4D parallelism. |
| [**trl-fine-tuning**](/docs/user-guide/skills/optional/mlops/mlops-training-trl-fine-tuning) | TRL: SFT, DPO, GRPO, RLOO reward modeling for LLM RLHF. |
| [**unsloth**](/docs/user-guide/skills/optional/mlops/mlops-training-unsloth) | Unsloth: 2-5x faster LoRA/QLoRA fine-tuning, less VRAM. |
| [**weights-and-biases**](/docs/user-guide/skills/optional/mlops/mlops-evaluation-weights-and-biases) | W&B: log ML experiments, sweeps, model registry, dashboards. |
| [**whisper**](/docs/user-guide/skills/optional/mlops/mlops-whisper) | Transcribe and translate speech in 99 languages. |

## payments

| Skill | Description |
|-------|-------------|
| [**mpp-agent**](/docs/user-guide/skills/optional/payments/payments-mpp-agent) | Pay HTTP 402 APIs via Machine Payments Protocol (MPP). |
| [**stripe-link-cli**](/docs/user-guide/skills/optional/payments/payments-stripe-link-cli) | Agent payments via Stripe Link — cards, SPT, approvals. |
| [**stripe-projects**](/docs/user-guide/skills/optional/payments/payments-stripe-projects) | Provision SaaS services + sync creds via Stripe Projects. |

## productivity

| Skill | Description |
|-------|-------------|
| [**canvas**](/docs/user-guide/skills/optional/productivity/productivity-canvas) | Fetch Canvas LMS courses and assignments via API token. |
| [**decision-questionnaire**](/docs/user-guide/skills/optional/productivity/productivity-decision-questionnaire) | Turn an unanswerable decision into a questionnaire doc. |
| [**here-now**](/docs/user-guide/skills/optional/productivity/productivity-here-now) | Publish sites to &#123;slug&#125;.here.now and store files in Drives. |
| [**memento-flashcards**](/docs/user-guide/skills/optional/productivity/productivity-memento-flashcards) | Spaced-repetition flashcards: create, review, quiz, export. |
| [**shop**](/docs/user-guide/skills/optional/productivity/productivity-shop) | Shop catalog search, checkout, order tracking, returns. |
| [**shopify**](/docs/user-guide/skills/optional/productivity/productivity-shopify) | Query Shopify Admin/Storefront GraphQL APIs via curl. |
| [**siyuan**](/docs/user-guide/skills/optional/productivity/productivity-siyuan) | Query and edit a SiYuan knowledge base via its API. |
| [**telephony**](/docs/user-guide/skills/optional/productivity/productivity-telephony) | Provision Twilio numbers, SMS/MMS, and AI outbound calls. |

## research

| Skill | Description |
|-------|-------------|
| [**bioinformatics**](/docs/user-guide/skills/optional/research/research-bioinformatics) | Gateway to 400+ genomics and computational biology skills. |
| [**blogwatcher**](/docs/user-guide/skills/optional/research/research-blogwatcher) | Monitor blogs and RSS/Atom feeds via blogwatcher-cli tool. |
| [**darwinian-evolver**](/docs/user-guide/skills/optional/research/research-darwinian-evolver) | Evolve prompts/regex/SQL/code with Imbue's evolution loop. |
| [**domain-intel**](/docs/user-guide/skills/optional/research/research-domain-intel) | Passive recon of subdomains, SSL certs, WHOIS, and DNS. |
| [**drug-discovery**](/docs/user-guide/skills/optional/research/research-drug-discovery) | Drug discovery: ChEMBL search, drug-likeness, interactions. |
| [**duckduckgo-search**](/docs/user-guide/skills/optional/research/research-duckduckgo-search) | Free keyless web, news, and image search via ddgs. |
| [**gitnexus-explorer**](/docs/user-guide/skills/optional/research/research-gitnexus-explorer) | Serve an interactive codebase knowledge graph web UI. |
| [**osint-investigation**](/docs/user-guide/skills/optional/research/research-osint-investigation) | Follow the money via public records and sanctions data. |
| [**parallel-cli**](/docs/user-guide/skills/optional/research/research-parallel-cli) | Agent-native web search, deep research, and enrichment. |
| [**pinecone-research**](/docs/user-guide/skills/optional/research/research-pinecone-research) | Agent RAG and long-term memory with Pinecone. |
| [**qmd**](/docs/user-guide/skills/optional/research/research-qmd) | Hybrid local search over notes, docs, and transcripts. |
| [**research-paper-writing**](/docs/user-guide/skills/optional/research/research-research-paper-writing) | Write ML papers for NeurIPS/ICML/ICLR: design→submit. |
| [**scrapling**](/docs/user-guide/skills/optional/research/research-scrapling) | Scrape sites with stealth browsing and Cloudflare bypass. |
| [**searxng-search**](/docs/user-guide/skills/optional/research/research-searxng-search) | Free keyless meta-search aggregating 70+ engines. |

## security

| Skill | Description |
|-------|-------------|
| [**1password**](/docs/user-guide/skills/optional/security/security-1password) | Set up op CLI, sign in, and read or inject secrets. |
| [**achieving-cmmc-level-2-compliance**](/docs/user-guide/skills/optional/security/security-achieving-cmmc-level-2-compliance) | Prepare a defense-contractor environment for CMMC Level 2 |
| [**acquiring-disk-image-with-dd-and-dcfldd**](/docs/user-guide/skills/optional/security/security-acquiring-disk-image-with-dd-and-dcfldd) | Create forensically sound bit-for-bit disk images with dd |
| [**analyzing-active-directory-acl-abuse**](/docs/user-guide/skills/optional/security/security-analyzing-active-directory-acl-abuse) | Detect dangerous ACL misconfigurations in Active Directory |
| [**analyzing-android-malware-with-apktool**](/docs/user-guide/skills/optional/security/security-analyzing-android-malware-with-apktool) | Perform static analysis of Android APK malware using |
| [**analyzing-api-gateway-access-logs**](/docs/user-guide/skills/optional/security/security-analyzing-api-gateway-access-logs) | Parses API Gateway access logs (AWS API Gateway, Kong |
| [**analyzing-apt-group-with-mitre-navigator**](/docs/user-guide/skills/optional/security/security-analyzing-apt-group-with-mitre-navigator) | Query ATT&CK data with attackcti, mitreattack-python, and |
| [**analyzing-azure-activity-logs-for-threats**](/docs/user-guide/skills/optional/security/security-analyzing-azure-activity-logs-for-threats) | Queries Azure Monitor activity logs and sign-in logs via |
| [**analyzing-bootkit-and-rootkit-samples**](/docs/user-guide/skills/optional/security/security-analyzing-bootkit-and-rootkit-samples) | Analyzes bootkit and advanced rootkit malware infecting the |
| [**analyzing-browser-forensics-with-hindsight**](/docs/user-guide/skills/optional/security/security-analyzing-browser-forensics-with-hindsight) | Parse Chromium-based browser databases with Hindsight to |
| [**analyzing-campaign-attribution-evidence**](/docs/user-guide/skills/optional/security/security-analyzing-campaign-attribution-evidence) | Systematically evaluate cyber-campaign evidence to |
| [**analyzing-certificate-transparency-for-phishing**](/docs/user-guide/skills/optional/security/security-analyzing-certificate-transparency-for-phishing) | Monitor Certificate Transparency logs using crt.sh and |
| [**analyzing-cloud-storage-access-patterns**](/docs/user-guide/skills/optional/security/security-analyzing-cloud-storage-access-patterns) | Detect abnormal access in AWS S3, GCS, and Azure Blob |
| [**analyzing-cobalt-strike-beacon-configuration**](/docs/user-guide/skills/optional/security/security-analyzing-cobalt-strike-beacon-configuration) | Extract and analyze Cobalt Strike beacon configuration from |
| [**analyzing-cobaltstrike-malleable-c2-profiles**](/docs/user-guide/skills/optional/security/security-analyzing-cobaltstrike-malleable-c2-profiles) | Parse and analyze Cobalt Strike Malleable C2 profiles with |
| [**analyzing-command-and-control-communication**](/docs/user-guide/skills/optional/security/security-analyzing-command-and-control-communication) | Analyzes malware C2 communication over HTTP, HTTPS, DNS |
| [**analyzing-cyber-kill-chain**](/docs/user-guide/skills/optional/security/security-analyzing-cyber-kill-chain) | Analyzes intrusion activity against the Lockheed Martin |
| [**analyzing-disk-image-with-autopsy**](/docs/user-guide/skills/optional/security/security-analyzing-disk-image-with-autopsy) | Perform comprehensive forensic analysis of raw (dd), E01 |
| [**analyzing-dns-logs-for-exfiltration**](/docs/user-guide/skills/optional/security/security-analyzing-dns-logs-for-exfiltration) | Analyzes DNS query logs to detect data exfiltration via DNS |
| [**analyzing-docker-container-forensics**](/docs/user-guide/skills/optional/security/security-analyzing-docker-container-forensics) | Investigate compromised Docker containers by analyzing |
| [**analyzing-email-headers-for-phishing-investigation**](/docs/user-guide/skills/optional/security/security-analyzing-email-headers-for-phishing-investigation) | Parse and analyze email headers (Received chain |
| [**analyzing-ethereum-smart-contract-vulnerabilities**](/docs/user-guide/skills/optional/security/security-analyzing-ethereum-smart-contract-vulnerabilities) | Perform static and symbolic analysis of Solidity smart |
| [**analyzing-golang-malware-with-ghidra**](/docs/user-guide/skills/optional/security/security-analyzing-golang-malware-with-ghidra) | Reverse engineer Go-compiled malware in Ghidra by parsing |
| [**analyzing-heap-spray-exploitation**](/docs/user-guide/skills/optional/security/security-analyzing-heap-spray-exploitation) | Detect and analyze heap spray attacks in memory dumps using |
| [**analyzing-indicators-of-compromise**](/docs/user-guide/skills/optional/security/security-analyzing-indicators-of-compromise) | Analyzes indicators of compromise (IOCs) including IP |
| [**analyzing-ios-app-security-with-objection**](/docs/user-guide/skills/optional/security/security-analyzing-ios-app-security-with-objection) | Runtime iOS app security testing with Objection (Frida) |
| [**analyzing-kubernetes-audit-logs**](/docs/user-guide/skills/optional/security/security-analyzing-kubernetes-audit-logs) | Parses Kubernetes API server audit logs (JSON lines) to |
| [**analyzing-linux-audit-logs-for-intrusion**](/docs/user-guide/skills/optional/security/security-analyzing-linux-audit-logs-for-intrusion) | Uses the Linux Audit framework (auditd) with ausearch and |
| [**analyzing-linux-elf-malware**](/docs/user-guide/skills/optional/security/security-analyzing-linux-elf-malware) | Analyze malicious Linux ELF binaries — botnets |
| [**analyzing-linux-kernel-rootkits**](/docs/user-guide/skills/optional/security/security-analyzing-linux-kernel-rootkits) | Detect kernel-level rootkits in Linux memory dumps using |
| [**analyzing-linux-system-artifacts**](/docs/user-guide/skills/optional/security/security-analyzing-linux-system-artifacts) | Examine Linux system artifacts (auth logs, cron/systemd |
| [**analyzing-lnk-file-and-jump-list-artifacts**](/docs/user-guide/skills/optional/security/security-analyzing-lnk-file-and-jump-list-artifacts) | Analyze Windows LNK shortcut files and Jump List artifacts |
| [**analyzing-macro-malware-in-office-documents**](/docs/user-guide/skills/optional/security/security-analyzing-macro-malware-in-office-documents) | Analyzes malicious VBA macros embedded in Microsoft Office |
| [**analyzing-malicious-pdf-with-peepdf**](/docs/user-guide/skills/optional/security/security-analyzing-malicious-pdf-with-peepdf) | Perform static analysis of malicious PDF documents using |
| [**analyzing-malicious-url-with-urlscan**](/docs/user-guide/skills/optional/security/security-analyzing-malicious-url-with-urlscan) | URLScan.io is a free service for scanning and analyzing |
| [**analyzing-malware-behavior-with-cuckoo-sandbox**](/docs/user-guide/skills/optional/security/security-analyzing-malware-behavior-with-cuckoo-sandbox) | Detonate malware samples in Cuckoo Sandbox to observe |
| [**analyzing-malware-family-relationships-with-malpedia**](/docs/user-guide/skills/optional/security/security-analyzing-malware-family-relationships-with-malpedia) | Query the Malpedia API to look up malware family aliases |
| [**analyzing-malware-persistence-with-autoruns**](/docs/user-guide/skills/optional/security/security-analyzing-malware-persistence-with-autoruns) | Use Sysinternals Autoruns to systematically enumerate and |
| [**analyzing-malware-sandbox-evasion-techniques**](/docs/user-guide/skills/optional/security/security-analyzing-malware-sandbox-evasion-techniques) | Detect sandbox and VM evasion techniques in malware samples |
| [**analyzing-memory-dumps-with-volatility**](/docs/user-guide/skills/optional/security/security-analyzing-memory-dumps-with-volatility) | Analyzes RAM memory dumps from compromised systems using |
| [**analyzing-memory-forensics-with-lime-and-volatility**](/docs/user-guide/skills/optional/security/security-analyzing-memory-forensics-with-lime-and-volatility) | Performs Linux memory acquisition using LiME (Linux Memory |
| [**analyzing-mft-for-deleted-file-recovery**](/docs/user-guide/skills/optional/security/security-analyzing-mft-for-deleted-file-recovery) | Analyze the NTFS Master File Table ($MFT) with MFTECmd |
| [**analyzing-network-covert-channels-in-malware**](/docs/user-guide/skills/optional/security/security-analyzing-network-covert-channels-in-malware) | Detect and analyze covert communication channels used by |
| [**analyzing-network-flow-data-with-netflow**](/docs/user-guide/skills/optional/security/security-analyzing-network-flow-data-with-netflow) | Parse NetFlow v9 and IPFIX records to detect volumetric |
| [**analyzing-network-packets-with-scapy**](/docs/user-guide/skills/optional/security/security-analyzing-network-packets-with-scapy) | Use Scapy to craft, send, sniff, and dissect |
| [**analyzing-network-traffic-for-incidents**](/docs/user-guide/skills/optional/security/security-analyzing-network-traffic-for-incidents) | Analyzes network traffic captures and flow data to identify |
| [**analyzing-network-traffic-of-malware**](/docs/user-guide/skills/optional/security/security-analyzing-network-traffic-of-malware) | Analyzes network traffic generated by malware during |
| [**analyzing-network-traffic-with-wireshark**](/docs/user-guide/skills/optional/security/security-analyzing-network-traffic-with-wireshark) | Captures and analyzes network packet data using Wireshark |
| [**analyzing-office365-audit-logs-for-compromise**](/docs/user-guide/skills/optional/security/security-analyzing-office365-audit-logs-for-compromise) | Parse Office 365 Unified Audit Logs via Microsoft Graph API |
| [**analyzing-outlook-pst-for-email-forensics**](/docs/user-guide/skills/optional/security/security-analyzing-outlook-pst-for-email-forensics) | Parse Microsoft Outlook PST and OST files using libpff and |
| [**analyzing-packed-malware-with-upx-unpacker**](/docs/user-guide/skills/optional/security/security-analyzing-packed-malware-with-upx-unpacker) | Identifies and unpacks UPX-packed malware samples |
| [**analyzing-pdf-malware-with-pdfid**](/docs/user-guide/skills/optional/security/security-analyzing-pdf-malware-with-pdfid) | Analyzes malicious PDF files using PDFiD, pdf-parser, and |
| [**analyzing-persistence-mechanisms-in-linux**](/docs/user-guide/skills/optional/security/security-analyzing-persistence-mechanisms-in-linux) | Scan Linux systems for persistence mechanisms including |
| [**analyzing-powershell-empire-artifacts**](/docs/user-guide/skills/optional/security/security-analyzing-powershell-empire-artifacts) | Detect PowerShell Empire post-exploitation framework |
| [**analyzing-powershell-script-block-logging**](/docs/user-guide/skills/optional/security/security-analyzing-powershell-script-block-logging) | Parse Windows PowerShell Script Block Logs (Event ID 4104) |
| [**analyzing-prefetch-files-for-execution-history**](/docs/user-guide/skills/optional/security/security-analyzing-prefetch-files-for-execution-history) | Parse Windows Prefetch files (versions 17, 23, 26, 30) with |
| [**analyzing-ransomware-encryption-mechanisms**](/docs/user-guide/skills/optional/security/security-analyzing-ransomware-encryption-mechanisms) | Analyzes encryption algorithms, key management, and file |
| [**analyzing-ransomware-leak-site-intelligence**](/docs/user-guide/skills/optional/security/security-analyzing-ransomware-leak-site-intelligence) | Safely monitor ransomware group Tor-hosted data leak sites |
| [**analyzing-ransomware-network-indicators**](/docs/user-guide/skills/optional/security/security-analyzing-ransomware-network-indicators) | Identify ransomware-related network indicators, including |
| [**analyzing-ransomware-payment-wallets**](/docs/user-guide/skills/optional/security/security-analyzing-ransomware-payment-wallets) | Traces ransomware cryptocurrency payment flows using |
| [**analyzing-sbom-for-supply-chain-vulnerabilities**](/docs/user-guide/skills/optional/security/security-analyzing-sbom-for-supply-chain-vulnerabilities) | Parses Software Bill of Materials (SBOM) in CycloneDX and |
| [**analyzing-security-logs-with-splunk**](/docs/user-guide/skills/optional/security/security-analyzing-security-logs-with-splunk) | Leverages Splunk Enterprise Security and SPL (Search |
| [**analyzing-slack-space-and-file-system-artifacts**](/docs/user-guide/skills/optional/security/security-analyzing-slack-space-and-file-system-artifacts) | Examine NTFS slack space, MFT entries, the USN Change |
| [**analyzing-supply-chain-malware-artifacts**](/docs/user-guide/skills/optional/security/security-analyzing-supply-chain-malware-artifacts) | Investigate supply chain attack artifacts including |
| [**analyzing-threat-actor-ttps-with-mitre-attack**](/docs/user-guide/skills/optional/security/security-analyzing-threat-actor-ttps-with-mitre-attack) | Systematically map threat actor behavior and observed IOCs |
| [**analyzing-threat-actor-ttps-with-mitre-navigator**](/docs/user-guide/skills/optional/security/security-analyzing-threat-actor-ttps-with-mitre-navigator) | Map advanced persistent threat (APT) group TTPs to the |
| [**analyzing-threat-intelligence-feeds**](/docs/user-guide/skills/optional/security/security-analyzing-threat-intelligence-feeds) | Analyzes structured and unstructured threat intelligence |
| [**analyzing-threat-landscape-with-misp**](/docs/user-guide/skills/optional/security/security-analyzing-threat-landscape-with-misp) | Query a MISP (Malware Information Sharing Platform) |
| [**analyzing-tls-certificate-transparency-logs**](/docs/user-guide/skills/optional/security/security-analyzing-tls-certificate-transparency-logs) | Queries Certificate Transparency logs via crt.sh and |
| [**analyzing-typosquatting-domains-with-dnstwist**](/docs/user-guide/skills/optional/security/security-analyzing-typosquatting-domains-with-dnstwist) | Generate domain permutations with dnstwist and check DNS |
| [**analyzing-uefi-bootkit-persistence**](/docs/user-guide/skills/optional/security/security-analyzing-uefi-bootkit-persistence) | Analyzes UEFI bootkit persistence (SPI flash implants, ESP |
| [**analyzing-usb-device-connection-history**](/docs/user-guide/skills/optional/security/security-analyzing-usb-device-connection-history) | Correlate Windows registry keys (USBSTOR, MountedDevices) |
| [**analyzing-web-server-logs-for-intrusion**](/docs/user-guide/skills/optional/security/security-analyzing-web-server-logs-for-intrusion) | Parse Apache and Nginx access logs to detect SQL injection |
| [**analyzing-windows-amcache-artifacts**](/docs/user-guide/skills/optional/security/security-analyzing-windows-amcache-artifacts) | Parses the Windows Amcache.hve registry hive with Eric |
| [**analyzing-windows-event-logs-in-splunk**](/docs/user-guide/skills/optional/security/security-analyzing-windows-event-logs-in-splunk) | Analyzes Windows Security, System, and Sysmon event logs in |
| [**analyzing-windows-lnk-files-for-artifacts**](/docs/user-guide/skills/optional/security/security-analyzing-windows-lnk-files-for-artifacts) | Parse Windows LNK shortcut files to extract target paths |
| [**analyzing-windows-prefetch-with-python**](/docs/user-guide/skills/optional/security/security-analyzing-windows-prefetch-with-python) | Parse Windows Prefetch (.pf) files with the windowsprefetch |
| [**analyzing-windows-registry-for-artifacts**](/docs/user-guide/skills/optional/security/security-analyzing-windows-registry-for-artifacts) | Extract and analyze Windows Registry hives with tools like |
| [**analyzing-windows-shellbag-artifacts**](/docs/user-guide/skills/optional/security/security-analyzing-windows-shellbag-artifacts) | Analyze Windows Shellbag (BagMRU) registry artifacts with |
| [**assessing-vector-and-embedding-weaknesses**](/docs/user-guide/skills/optional/security/security-assessing-vector-and-embedding-weaknesses) | Test RAG vector stores (Pinecone, Qdrant, Weaviate, Chroma |
| [**attacking-entra-id-with-roadtools**](/docs/user-guide/skills/optional/security/security-attacking-entra-id-with-roadtools) | Enumerate Microsoft Entra ID (Azure AD) tenants with |
| [**attacking-oauth-with-device-code-phishing**](/docs/user-guide/skills/optional/security/security-attacking-oauth-with-device-code-phishing) | Run OAuth 2.0 device-code and illicit-consent phishing |
| [**auditing-aws-s3-bucket-permissions**](/docs/user-guide/skills/optional/security/security-auditing-aws-s3-bucket-permissions) | Systematically audit AWS S3 bucket permissions to identify |
| [**auditing-azure-active-directory-configuration**](/docs/user-guide/skills/optional/security/security-auditing-azure-active-directory-configuration) | Auditing Microsoft Entra ID (Azure Active Directory) |
| [**auditing-cloud-with-cis-benchmarks**](/docs/user-guide/skills/optional/security/security-auditing-cloud-with-cis-benchmarks) | Audit AWS, Azure, and GCP environments against the CIS |
| [**auditing-entra-id-with-aadinternals**](/docs/user-guide/skills/optional/security/security-auditing-entra-id-with-aadinternals) | Drive the AADInternals PowerShell toolkit to perform |
| [**auditing-foundry-smart-contract-security**](/docs/user-guide/skills/optional/security/security-auditing-foundry-smart-contract-security) | Pre-deployment security audit of Solidity smart contracts |
| [**auditing-gcp-iam-permissions**](/docs/user-guide/skills/optional/security/security-auditing-gcp-iam-permissions) | Auditing Google Cloud Platform IAM permissions to identify |
| [**auditing-kubernetes-cluster-rbac**](/docs/user-guide/skills/optional/security/security-auditing-kubernetes-cluster-rbac) | Auditing Kubernetes cluster RBAC configurations to identify |
| [**auditing-kubernetes-rbac-privilege-escalation**](/docs/user-guide/skills/optional/security/security-auditing-kubernetes-rbac-privilege-escalation) | Finds over-permissive RBAC roles and service-account token |
| [**auditing-mcp-servers-for-tool-poisoning**](/docs/user-guide/skills/optional/security/security-auditing-mcp-servers-for-tool-poisoning) | Audit MCP servers for tool poisoning, tool shadowing, rug |
| [**auditing-terraform-infrastructure-for-security**](/docs/user-guide/skills/optional/security/security-auditing-terraform-infrastructure-for-security) | Auditing Terraform infrastructure-as-code for security |
| [**auditing-tls-certificate-transparency-logs**](/docs/user-guide/skills/optional/security/security-auditing-tls-certificate-transparency-logs) | Monitors Certificate Transparency (CT) logs to detect |
| [**auditing-uefi-firmware-with-chipsec**](/docs/user-guide/skills/optional/security/security-auditing-uefi-firmware-with-chipsec) | Use Intel CHIPSEC to assess platform firmware |
| [**automating-ioc-enrichment**](/docs/user-guide/skills/optional/security/security-automating-ioc-enrichment) | Automates the enrichment of raw indicators of compromise |
| [**benchmarking-kubernetes-with-kube-bench**](/docs/user-guide/skills/optional/security/security-benchmarking-kubernetes-with-kube-bench) | Installs and runs the kube-bench tool against a Kubernetes |
| [**building-adversary-infrastructure-tracking-system**](/docs/user-guide/skills/optional/security/security-building-adversary-infrastructure-tracking-system) | Build an automated adversary infrastructure tracking system |
| [**building-attack-pattern-library-from-cti-reports**](/docs/user-guide/skills/optional/security/security-building-attack-pattern-library-from-cti-reports) | Parse cyber threat intelligence reports (Mandiant |
| [**building-automated-malware-submission-pipeline**](/docs/user-guide/skills/optional/security/security-building-automated-malware-submission-pipeline) | Builds an automated malware submission and analysis |
| [**building-cloud-siem-with-sentinel**](/docs/user-guide/skills/optional/security/security-building-cloud-siem-with-sentinel) | Deploy Microsoft Sentinel as a cloud-native SIEM/SOAR by |
| [**building-detection-rule-with-splunk-spl**](/docs/user-guide/skills/optional/security/security-building-detection-rule-with-splunk-spl) | Build effective detection rules using Splunk Search |
| [**building-detection-rules-with-sigma**](/docs/user-guide/skills/optional/security/security-building-detection-rules-with-sigma) | Builds vendor-agnostic detection rules using the Sigma rule |
| [**building-devsecops-pipeline-with-gitlab-ci**](/docs/user-guide/skills/optional/security/security-building-devsecops-pipeline-with-gitlab-ci) | Configure a GitLab CI/CD pipeline that embeds SAST |
| [**building-identity-federation-with-saml-azure-ad**](/docs/user-guide/skills/optional/security/security-building-identity-federation-with-saml-azure-ad) | Configure SAML 2.0 identity federation between on-premises |
| [**building-identity-governance-lifecycle-process**](/docs/user-guide/skills/optional/security/security-building-identity-governance-lifecycle-process) | Design identity governance and lifecycle (IGA) programs on |
| [**building-incident-response-dashboard**](/docs/user-guide/skills/optional/security/security-building-incident-response-dashboard) | Builds real-time incident response dashboards in Splunk |
| [**building-incident-response-playbook**](/docs/user-guide/skills/optional/security/security-building-incident-response-playbook) | Designs and documents structured incident response |
| [**building-incident-timeline-with-timesketch**](/docs/user-guide/skills/optional/security/security-building-incident-timeline-with-timesketch) | Build collaborative forensic incident timelines using |
| [**building-ioc-defanging-and-sharing-pipeline**](/docs/user-guide/skills/optional/security/security-building-ioc-defanging-and-sharing-pipeline) | Build an automated pipeline that ingests raw IOCs (URLs |
| [**building-ioc-enrichment-pipeline-with-opencti**](/docs/user-guide/skills/optional/security/security-building-ioc-enrichment-pipeline-with-opencti) | Build an automated IOC enrichment pipeline on OpenCTI (STIX |
| [**building-malware-incident-communication-template**](/docs/user-guide/skills/optional/security/security-building-malware-incident-communication-template) | Build structured communication templates for malware |
| [**building-patch-tuesday-response-process**](/docs/user-guide/skills/optional/security/security-building-patch-tuesday-response-process) | Establish a repeatable operational process for triaging |
| [**building-phishing-reporting-button-workflow**](/docs/user-guide/skills/optional/security/security-building-phishing-reporting-button-workflow) | Implement a phishing report button (Microsoft 365 built-in |
| [**building-ransomware-playbook-with-cisa-framework**](/docs/user-guide/skills/optional/security/security-building-ransomware-playbook-with-cisa-framework) | Builds a structured ransomware incident response playbook |
| [**building-role-mining-for-rbac-optimization**](/docs/user-guide/skills/optional/security/security-building-role-mining-for-rbac-optimization) | Apply bottom-up and top-down role mining techniques |
| [**building-soc-escalation-matrix**](/docs/user-guide/skills/optional/security/security-building-soc-escalation-matrix) | Build a structured SOC escalation matrix defining severity |
| [**building-soc-metrics-and-kpi-tracking**](/docs/user-guide/skills/optional/security/security-building-soc-metrics-and-kpi-tracking) | Builds SOC performance metrics and KPI tracking dashboards |
| [**building-soc-playbook-for-ransomware**](/docs/user-guide/skills/optional/security/security-building-soc-playbook-for-ransomware) | Builds a structured SOC incident response playbook for |
| [**building-super-timelines-with-plaso**](/docs/user-guide/skills/optional/security/security-building-super-timelines-with-plaso) | Generate forensic super-timelines with Plaso's |
| [**building-threat-actor-profile-from-osint**](/docs/user-guide/skills/optional/security/security-building-threat-actor-profile-from-osint) | Build threat actor profiles by collecting OSINT from vendor |
| [**building-threat-feed-aggregation-with-misp**](/docs/user-guide/skills/optional/security/security-building-threat-feed-aggregation-with-misp) | Deploy MISP via Docker and configure feeds from sources |
| [**building-threat-hunt-hypothesis-framework**](/docs/user-guide/skills/optional/security/security-building-threat-hunt-hypothesis-framework) | Build a systematic threat-hunt workflow that turns threat |
| [**building-threat-intelligence-enrichment-in-splunk**](/docs/user-guide/skills/optional/security/security-building-threat-intelligence-enrichment-in-splunk) | Build automated IOC enrichment pipelines in Splunk |
| [**building-threat-intelligence-feed-integration**](/docs/user-guide/skills/optional/security/security-building-threat-intelligence-feed-integration) | Builds automated threat intelligence feed integration |
| [**building-threat-intelligence-platform**](/docs/user-guide/skills/optional/security/security-building-threat-intelligence-platform) | Design and deploy a Threat Intelligence Platform (TIP) by |
| [**building-vulnerability-aging-and-sla-tracking**](/docs/user-guide/skills/optional/security/security-building-vulnerability-aging-and-sla-tracking) | Implement a vulnerability aging dashboard and SLA tracking |
| [**building-vulnerability-dashboard-with-defectdojo**](/docs/user-guide/skills/optional/security/security-building-vulnerability-dashboard-with-defectdojo) | Deploy DefectDojo as a centralized vulnerability management |
| [**building-vulnerability-exception-tracking-system**](/docs/user-guide/skills/optional/security/security-building-vulnerability-exception-tracking-system) | Build a vulnerability exception and risk acceptance |
| [**building-vulnerability-scanning-workflow**](/docs/user-guide/skills/optional/security/security-building-vulnerability-scanning-workflow) | Builds a structured vulnerability scanning workflow using |
| [**bypassing-authentication-with-forced-browsing**](/docs/user-guide/skills/optional/security/security-bypassing-authentication-with-forced-browsing) | Discovering and accessing unprotected pages, APIs, and |
| [**collecting-indicators-of-compromise**](/docs/user-guide/skills/optional/security/security-collecting-indicators-of-compromise) | Systematically collects, categorizes, and distributes |
| [**collecting-open-source-intelligence**](/docs/user-guide/skills/optional/security/security-collecting-open-source-intelligence) | Collects and synthesizes open-source intelligence (OSINT) |
| [**collecting-threat-intelligence-with-misp**](/docs/user-guide/skills/optional/security/security-collecting-threat-intelligence-with-misp) | Deploy MISP, configure threat feeds (MISP community |
| [**collecting-volatile-evidence-from-compromised-host**](/docs/user-guide/skills/optional/security/security-collecting-volatile-evidence-from-compromised-host) | Collect volatile forensic evidence from a compromised host |
| [**conducting-cloud-incident-response**](/docs/user-guide/skills/optional/security/security-conducting-cloud-incident-response) | Respond to security incidents in AWS, Azure, and GCP via |
| [**conducting-cloud-penetration-testing**](/docs/user-guide/skills/optional/security/security-conducting-cloud-penetration-testing) | This skill outlines methodologies for performing authorized |
| [**conducting-cyber-risk-assessment-with-nist-800-30**](/docs/user-guide/skills/optional/security/security-conducting-cyber-risk-assessment-with-nist-800-30) | Conduct a defensible cybersecurity risk assessment using |
| [**conducting-gdpr-compliance-assessment**](/docs/user-guide/skills/optional/security/security-conducting-gdpr-compliance-assessment) | Conduct comprehensive GDPR compliance assessments by |
| [**conducting-malware-incident-response**](/docs/user-guide/skills/optional/security/security-conducting-malware-incident-response) | Respond to malware infections across enterprise endpoints |
| [**conducting-man-in-the-middle-attack-simulation**](/docs/user-guide/skills/optional/security/security-conducting-man-in-the-middle-attack-simulation) | Simulates man-in-the-middle attacks using Ettercap |
| [**conducting-memory-forensics-with-volatility**](/docs/user-guide/skills/optional/security/security-conducting-memory-forensics-with-volatility) | Performs memory forensics analysis using Volatility 3 to |
| [**conducting-phishing-incident-response**](/docs/user-guide/skills/optional/security/security-conducting-phishing-incident-response) | Respond to phishing incidents by analyzing reported emails |
| [**conducting-post-incident-lessons-learned**](/docs/user-guide/skills/optional/security/security-conducting-post-incident-lessons-learned) | Facilitate structured post-incident reviews to identify |
| [**configuring-active-directory-tiered-model**](/docs/user-guide/skills/optional/security/security-configuring-active-directory-tiered-model) | Implement Microsoft's Enhanced Security Admin Environment |
| [**configuring-aws-verified-access-for-ztna**](/docs/user-guide/skills/optional/security/security-configuring-aws-verified-access-for-ztna) | Configure AWS Verified Access to provide VPN-less zero |
| [**configuring-certificate-authority-with-openssl**](/docs/user-guide/skills/optional/security/security-configuring-certificate-authority-with-openssl) | Build a two-tier PKI Certificate Authority hierarchy |
| [**configuring-host-based-intrusion-detection**](/docs/user-guide/skills/optional/security/security-configuring-host-based-intrusion-detection) | Configures host-based intrusion detection systems (HIDS) to |
| [**configuring-hsm-for-key-storage**](/docs/user-guide/skills/optional/security/security-configuring-hsm-for-key-storage) | Configures Hardware Security Modules for cryptographic key |
| [**configuring-identity-aware-proxy-with-google-iap**](/docs/user-guide/skills/optional/security/security-configuring-identity-aware-proxy-with-google-iap) | Configures Google Cloud Identity-Aware Proxy (IAP) via |
| [**configuring-ldap-security-hardening**](/docs/user-guide/skills/optional/security/security-configuring-ldap-security-hardening) | Hardens LDAP directory services against credential |
| [**configuring-microsegmentation-for-zero-trust**](/docs/user-guide/skills/optional/security/security-configuring-microsegmentation-for-zero-trust) | Configures microsegmentation policies to enforce |
| [**configuring-multi-factor-authentication-with-duo**](/docs/user-guide/skills/optional/security/security-configuring-multi-factor-authentication-with-duo) | Deploys Cisco Duo multi-factor authentication across |
| [**configuring-network-segmentation-with-vlans**](/docs/user-guide/skills/optional/security/security-configuring-network-segmentation-with-vlans) | Designs and implements VLAN-based (802.1Q) network |
| [**configuring-oauth2-authorization-flow**](/docs/user-guide/skills/optional/security/security-configuring-oauth2-authorization-flow) | Configures secure OAuth 2.0 authorization flows, including |
| [**configuring-pfsense-firewall-rules**](/docs/user-guide/skills/optional/security/security-configuring-pfsense-firewall-rules) | Configures pfSense firewall rules, NAT policies |
| [**configuring-snort-ids-for-intrusion-detection**](/docs/user-guide/skills/optional/security/security-configuring-snort-ids-for-intrusion-detection) | Installs, configures, and tunes Snort 3 to monitor network |
| [**configuring-suricata-for-network-monitoring**](/docs/user-guide/skills/optional/security/security-configuring-suricata-for-network-monitoring) | Deploys and configures Suricata IDS/IPS with Emerging |
| [**configuring-tls-1-3-for-secure-communications**](/docs/user-guide/skills/optional/security/security-configuring-tls-1-3-for-secure-communications) | Configures TLS 1.3 (RFC 8446) on servers, covering cipher |
| [**configuring-windows-defender-advanced-settings**](/docs/user-guide/skills/optional/security/security-configuring-windows-defender-advanced-settings) | Configures Microsoft Defender for Endpoint (MDE) advanced |
| [**configuring-windows-event-logging-for-detection**](/docs/user-guide/skills/optional/security/security-configuring-windows-event-logging-for-detection) | Configures Windows Event Logging with advanced audit |
| [**configuring-zscaler-private-access-for-ztna**](/docs/user-guide/skills/optional/security/security-configuring-zscaler-private-access-for-ztna) | Configures Zscaler Private Access (ZPA) to replace |
| [**containing-active-breach**](/docs/user-guide/skills/optional/security/security-containing-active-breach) | Executes containment strategies to stop active adversary |
| [**continuous-llm-red-teaming-with-promptfoo**](/docs/user-guide/skills/optional/security/security-continuous-llm-red-teaming-with-promptfoo) | Wires Promptfoo and DeepTeam into CI/CD for automated |
| [**correlating-security-events-in-qradar**](/docs/user-guide/skills/optional/security/security-correlating-security-events-in-qradar) | Correlates security events in IBM QRadar SIEM using AQL |
| [**correlating-threat-campaigns**](/docs/user-guide/skills/optional/security/security-correlating-threat-campaigns) | Correlates disparate security incidents, IOCs, and |
| [**defending-llms-with-guardrails**](/docs/user-guide/skills/optional/security/security-defending-llms-with-guardrails) | Deploys Llama Guard 3 safety classification, NeMo |
| [**deobfuscating-javascript-malware**](/docs/user-guide/skills/optional/security/security-deobfuscating-javascript-malware) | Deobfuscates malicious JavaScript found in phishing pages |
| [**deobfuscating-powershell-obfuscated-malware**](/docs/user-guide/skills/optional/security/security-deobfuscating-powershell-obfuscated-malware) | Systematically deobfuscates multi-layer PowerShell malware |
| [**deploying-active-directory-honeytokens**](/docs/user-guide/skills/optional/security/security-deploying-active-directory-honeytokens) | Deploys deception-based honeytokens in Active Directory |
| [**deploying-cloud-deception-with-decoy-resources**](/docs/user-guide/skills/optional/security/security-deploying-cloud-deception-with-decoy-resources) | Deploy cloud-native deception across AWS, Azure, and GCP |
| [**deploying-cloudflare-access-for-zero-trust**](/docs/user-guide/skills/optional/security/security-deploying-cloudflare-access-for-zero-trust) | Deploys Cloudflare Access with Cloudflare Tunnel for zero |
| [**deploying-decoy-files-for-ransomware-detection**](/docs/user-guide/skills/optional/security/security-deploying-decoy-files-for-ransomware-detection) | Deploys canary files (honeytokens) across file systems to |
| [**deploying-edr-agent-with-crowdstrike**](/docs/user-guide/skills/optional/security/security-deploying-edr-agent-with-crowdstrike) | Deploys and configures CrowdStrike Falcon EDR agents across |
| [**deploying-honeytokens-and-canarytokens**](/docs/user-guide/skills/optional/security/security-deploying-honeytokens-and-canarytokens) | Plants Canarytokens-based decoy artifacts (honey |
| [**deploying-osquery-for-endpoint-monitoring**](/docs/user-guide/skills/optional/security/security-deploying-osquery-for-endpoint-monitoring) | Deploys and configures osquery for real-time endpoint |
| [**deploying-palo-alto-prisma-access-zero-trust**](/docs/user-guide/skills/optional/security/security-deploying-palo-alto-prisma-access-zero-trust) | Deploys Palo Alto Networks Prisma Access for SASE-based |
| [**deploying-ransomware-canary-files**](/docs/user-guide/skills/optional/security/security-deploying-ransomware-canary-files) | Deploys and monitors ransomware canary files using Python's |
| [**deploying-software-defined-perimeter**](/docs/user-guide/skills/optional/security/security-deploying-software-defined-perimeter) | Deploys a Software-Defined Perimeter per the CSA v2.0 |
| [**deploying-tailscale-for-zero-trust-vpn**](/docs/user-guide/skills/optional/security/security-deploying-tailscale-for-zero-trust-vpn) | Deploys and configures Tailscale (or self-hosted Headscale) |
| [**designing-adversary-engagement-with-mitre-engage**](/docs/user-guide/skills/optional/security/security-designing-adversary-engagement-with-mitre-engage) | Plan, run, and measure an adversary engagement operation |
| [**detecting-ai-model-prompt-injection-attacks**](/docs/user-guide/skills/optional/security/security-detecting-ai-model-prompt-injection-attacks) | Detects prompt injection using regex signature matching |
| [**detecting-anomalies-in-industrial-control-systems**](/docs/user-guide/skills/optional/security/security-detecting-anomalies-in-industrial-control-systems) | Deploys anomaly detection for OT/ICS environments using |
| [**detecting-anomalous-authentication-patterns**](/docs/user-guide/skills/optional/security/security-detecting-anomalous-authentication-patterns) | Detects anomalous authentication patterns using UEBA |
| [**detecting-api-enumeration-attacks**](/docs/user-guide/skills/optional/security/security-detecting-api-enumeration-attacks) | Detect API enumeration attacks (BOLA/IDOR, OWASP API1:2023) |
| [**detecting-arp-poisoning-in-network-traffic**](/docs/user-guide/skills/optional/security/security-detecting-arp-poisoning-in-network-traffic) | Detect Layer 2 ARP poisoning/spoofing by deploying |
| [**detecting-attacks-on-historian-servers**](/docs/user-guide/skills/optional/security/security-detecting-attacks-on-historian-servers) | Detect cyber attacks on OT historian servers (OSIsoft PI |
| [**detecting-attacks-on-scada-systems**](/docs/user-guide/skills/optional/security/security-detecting-attacks-on-scada-systems) | This skill covers detecting cyber attacks targeting |
| [**detecting-aws-cloudtrail-anomalies**](/docs/user-guide/skills/optional/security/security-detecting-aws-cloudtrail-anomalies) | Detect unusual API call patterns in AWS CloudTrail logs |
| [**detecting-aws-credential-exposure-with-trufflehog**](/docs/user-guide/skills/optional/security/security-detecting-aws-credential-exposure-with-trufflehog) | Scan source code repositories, CI/CD pipelines, and |
| [**detecting-aws-guardduty-findings-automation**](/docs/user-guide/skills/optional/security/security-detecting-aws-guardduty-findings-automation) | Build automated AWS GuardDuty finding response pipelines |
| [**detecting-aws-iam-privilege-escalation**](/docs/user-guide/skills/optional/security/security-detecting-aws-iam-privilege-escalation) | Detect AWS IAM privilege escalation paths using boto3 and |
| [**detecting-azure-lateral-movement**](/docs/user-guide/skills/optional/security/security-detecting-azure-lateral-movement) | Detect lateral movement in Azure AD/Entra ID environments |
| [**detecting-azure-service-principal-abuse**](/docs/user-guide/skills/optional/security/security-detecting-azure-service-principal-abuse) | Detect Azure service principal abuse in Microsoft Entra ID |
| [**detecting-azure-storage-account-misconfigurations**](/docs/user-guide/skills/optional/security/security-detecting-azure-storage-account-misconfigurations) | Audit Azure Blob and ADLS storage accounts for public |
| [**detecting-beaconing-patterns-with-zeek**](/docs/user-guide/skills/optional/security/security-detecting-beaconing-patterns-with-zeek) | Performs statistical analysis of Zeek conn.log connection |
| [**detecting-bluetooth-low-energy-attacks**](/docs/user-guide/skills/optional/security/security-detecting-bluetooth-low-energy-attacks) | Detects and analyzes Bluetooth Low Energy (BLE) security |
| [**detecting-broken-object-property-level-authorization**](/docs/user-guide/skills/optional/security/security-detecting-broken-object-property-level-authorization) | Detect and test for OWASP API3:2023 Broken Object Property |
| [**detecting-business-email-compromise**](/docs/user-guide/skills/optional/security/security-detecting-business-email-compromise) | Detect Business Email Compromise (BEC) fraud, where |
| [**detecting-business-email-compromise-with-ai**](/docs/user-guide/skills/optional/security/security-detecting-business-email-compromise-with-ai) | Deploy AI and NLP-powered detection systems to identify |
| [**detecting-cloud-threats-with-guardduty**](/docs/user-guide/skills/optional/security/security-detecting-cloud-threats-with-guardduty) | Deploy and operationalize Amazon GuardDuty, covering |
| [**detecting-command-and-control-over-dns**](/docs/user-guide/skills/optional/security/security-detecting-command-and-control-over-dns) | Detect command-and-control (C2) traffic tunneled over DNS |
| [**detecting-compromised-cloud-credentials**](/docs/user-guide/skills/optional/security/security-detecting-compromised-cloud-credentials) | Detect compromised cloud credentials across AWS, Azure, and |
| [**detecting-container-drift-at-runtime**](/docs/user-guide/skills/optional/security/security-detecting-container-drift-at-runtime) | Detects unauthorized runtime drift in containers by |
| [**detecting-container-escape-attempts**](/docs/user-guide/skills/optional/security/security-detecting-container-escape-attempts) | Detects container escape at runtime across tooling - |
| [**detecting-container-escape-with-falco-rules**](/docs/user-guide/skills/optional/security/security-detecting-container-escape-with-falco-rules) | Writes and tunes Falco rule syntax for container escape |
| [**detecting-container-runtime-threats-with-falco**](/docs/user-guide/skills/optional/security/security-detecting-container-runtime-threats-with-falco) | Deploys and operates Falco with the modern eBPF driver in |
| [**detecting-credential-dumping-techniques**](/docs/user-guide/skills/optional/security/security-detecting-credential-dumping-techniques) | Detect LSASS credential dumping, SAM database extraction |
| [**detecting-cryptomining-in-cloud**](/docs/user-guide/skills/optional/security/security-detecting-cryptomining-in-cloud) | This skill teaches security teams how to detect and respond |
| [**detecting-data-and-model-poisoning**](/docs/user-guide/skills/optional/security/security-detecting-data-and-model-poisoning) | Identify poisoned training data and backdoored ML models |
| [**detecting-dcsync-attack-in-active-directory**](/docs/user-guide/skills/optional/security/security-detecting-dcsync-attack-in-active-directory) | Detect DCSync attacks (MITRE T1003.006) where adversaries |
| [**detecting-deepfake-audio-in-vishing-attacks**](/docs/user-guide/skills/optional/security/security-detecting-deepfake-audio-in-vishing-attacks) | Detect AI-generated deepfake audio used in voice phishing |
| [**detecting-dependency-confusion**](/docs/user-guide/skills/optional/security/security-detecting-dependency-confusion) | Detect and prevent dependency confusion |
| [**detecting-dll-sideloading-attacks**](/docs/user-guide/skills/optional/security/security-detecting-dll-sideloading-attacks) | Detect DLL side-loading and search-order hijacking (MITRE |
| [**detecting-dnp3-protocol-anomalies**](/docs/user-guide/skills/optional/security/security-detecting-dnp3-protocol-anomalies) | Detect anomalies in DNP3 communications used in SCADA/ICS |
| [**detecting-dns-exfiltration-with-dns-query-analysis**](/docs/user-guide/skills/optional/security/security-detecting-dns-exfiltration-with-dns-query-analysis) | Detect data exfiltration via DNS tunneling (tools like |
| [**detecting-email-account-compromise**](/docs/user-guide/skills/optional/security/security-detecting-email-account-compromise) | Detect compromised O365 and Google Workspace email accounts |
| [**detecting-email-forwarding-rules-attack**](/docs/user-guide/skills/optional/security/security-detecting-email-forwarding-rules-attack) | Detect malicious inbox/mail-flow forwarding rules that |
| [**detecting-entra-offensive-tools-in-graph-logs**](/docs/user-guide/skills/optional/security/security-detecting-entra-offensive-tools-in-graph-logs) | Hunt AADGraphActivityLogs and MicrosoftGraphActivityLogs in |
| [**detecting-evasion-techniques-in-endpoint-logs**](/docs/user-guide/skills/optional/security/security-detecting-evasion-techniques-in-endpoint-logs) | Detects defense evasion techniques used by adversaries in |
| [**detecting-exfiltration-over-dns-with-zeek**](/docs/user-guide/skills/optional/security/security-detecting-exfiltration-over-dns-with-zeek) | Detect DNS-based data exfiltration by analyzing Zeek |
| [**detecting-fileless-attacks-on-endpoints**](/docs/user-guide/skills/optional/security/security-detecting-fileless-attacks-on-endpoints) | Detects fileless malware and in-memory attacks that execute |
| [**detecting-fileless-malware-techniques**](/docs/user-guide/skills/optional/security/security-detecting-fileless-malware-techniques) | Detects and analyzes fileless malware that operates |
| [**detecting-golden-ticket-attacks-in-kerberos-logs**](/docs/user-guide/skills/optional/security/security-detecting-golden-ticket-attacks-in-kerberos-logs) | Detect Golden Ticket attacks in Active Directory using |
| [**detecting-golden-ticket-forgery**](/docs/user-guide/skills/optional/security/security-detecting-golden-ticket-forgery) | Detect Kerberos Golden Ticket forgery (e.g |
| [**detecting-indirect-prompt-injection**](/docs/user-guide/skills/optional/security/security-detecting-indirect-prompt-injection) | Detect and defend against indirect prompt injection hidden |
| [**detecting-insider-data-exfiltration-via-dlp**](/docs/user-guide/skills/optional/security/security-detecting-insider-data-exfiltration-via-dlp) | Detects insider data exfiltration by analyzing DLP policy |
| [**detecting-insider-threat-behaviors**](/docs/user-guide/skills/optional/security/security-detecting-insider-threat-behaviors) | Detect insider threat behavioral indicators including |
| [**detecting-insider-threat-with-ueba**](/docs/user-guide/skills/optional/security/security-detecting-insider-threat-with-ueba) | Implement User and Entity Behavior Analytics (UEBA) using |
| [**detecting-kerberoasting-attacks**](/docs/user-guide/skills/optional/security/security-detecting-kerberoasting-attacks) | Detect Kerberoasting attacks by monitoring for anomalous |
| [**detecting-lateral-movement-in-network**](/docs/user-guide/skills/optional/security/security-detecting-lateral-movement-in-network) | Identifies lateral movement techniques in enterprise |
| [**detecting-lateral-movement-with-splunk**](/docs/user-guide/skills/optional/security/security-detecting-lateral-movement-with-splunk) | Detect adversary lateral movement across networks using |
| [**detecting-lateral-movement-with-zeek**](/docs/user-guide/skills/optional/security/security-detecting-lateral-movement-with-zeek) | Detect lateral movement in network traffic using Zeek |
| [**detecting-living-off-the-land-attacks**](/docs/user-guide/skills/optional/security/security-detecting-living-off-the-land-attacks) | Detect abuse of legitimate Windows binaries (LOLBins) used |
| [**detecting-living-off-the-land-with-lolbas**](/docs/user-guide/skills/optional/security/security-detecting-living-off-the-land-with-lolbas) | Detect Living Off the Land Binaries (LOLBins/LOLBAS) abuse |
| [**detecting-malicious-npm-packages**](/docs/user-guide/skills/optional/security/security-detecting-malicious-npm-packages) | Triage npm packages and lockfiles for install-script |
| [**detecting-malicious-scheduled-tasks-with-sysmon**](/docs/user-guide/skills/optional/security/security-detecting-malicious-scheduled-tasks-with-sysmon) | Detect malicious scheduled task creation and modification |
| [**detecting-mimikatz-execution-patterns**](/docs/user-guide/skills/optional/security/security-detecting-mimikatz-execution-patterns) | Detect Mimikatz credential-dumping activity via |
| [**detecting-misconfigured-azure-storage**](/docs/user-guide/skills/optional/security/security-detecting-misconfigured-azure-storage) | Audit Azure Storage accounts for public blob containers |
| [**detecting-mobile-malware-behavior**](/docs/user-guide/skills/optional/security/security-detecting-mobile-malware-behavior) | Detects and analyzes malicious behavior in mobile |
| [**detecting-modbus-command-injection-attacks**](/docs/user-guide/skills/optional/security/security-detecting-modbus-command-injection-attacks) | Detect command injection against Modbus TCP/RTU in |
| [**detecting-modbus-protocol-anomalies**](/docs/user-guide/skills/optional/security/security-detecting-modbus-protocol-anomalies) | Detect anomalies in Modbus/TCP and Modbus RTU industrial |
| [**detecting-model-extraction-attacks**](/docs/user-guide/skills/optional/security/security-detecting-model-extraction-attacks) | Detect MITRE ATLAS AML.T0024 attacks (model stealing |
| [**detecting-network-anomalies-with-zeek**](/docs/user-guide/skills/optional/security/security-detecting-network-anomalies-with-zeek) | Deploy and configure Zeek (formerly Bro) to passively |
| [**detecting-network-scanning-with-ids-signatures**](/docs/user-guide/skills/optional/security/security-detecting-network-scanning-with-ids-signatures) | Detect network reconnaissance and port scanning using |
| [**detecting-ntlm-relay-with-event-correlation**](/docs/user-guide/skills/optional/security/security-detecting-ntlm-relay-with-event-correlation) | Detect NTLM relay attacks (T1557.001) by correlating |
| [**detecting-oauth-token-theft**](/docs/user-guide/skills/optional/security/security-detecting-oauth-token-theft) | Detect and respond to OAuth token theft and replay in |
| [**detecting-pass-the-hash-attacks**](/docs/user-guide/skills/optional/security/security-detecting-pass-the-hash-attacks) | Detect Pass-the-Hash (T1550.002) attacks by analyzing NTLM |
| [**detecting-pass-the-ticket-attacks**](/docs/user-guide/skills/optional/security/security-detecting-pass-the-ticket-attacks) | Detect Kerberos Pass-the-Ticket (PtT) attacks by analyzing |
| [**detecting-port-scanning-with-fail2ban**](/docs/user-guide/skills/optional/security/security-detecting-port-scanning-with-fail2ban) | Configures Fail2ban with custom filters and actions to |
| [**detecting-privilege-escalation-attempts**](/docs/user-guide/skills/optional/security/security-detecting-privilege-escalation-attempts) | Detect privilege escalation attempts across Windows and |
| [**detecting-privilege-escalation-in-kubernetes-pods**](/docs/user-guide/skills/optional/security/security-detecting-privilege-escalation-in-kubernetes-pods) | Detects and prevents privilege escalation inside Kubernetes |
| [**detecting-process-hollowing-technique**](/docs/user-guide/skills/optional/security/security-detecting-process-hollowing-technique) | Detect process hollowing (MITRE T1055.012) by analyzing |
| [**detecting-process-injection-techniques**](/docs/user-guide/skills/optional/security/security-detecting-process-injection-techniques) | Detects and analyzes process injection techniques used by |
| [**detecting-qr-code-phishing-with-email-security**](/docs/user-guide/skills/optional/security/security-detecting-qr-code-phishing-with-email-security) | Detect and prevent QR code phishing (quishing) attacks that |
| [**detecting-ransomware-encryption-behavior**](/docs/user-guide/skills/optional/security/security-detecting-ransomware-encryption-behavior) | Detects ransomware encryption activity in real time using |
| [**detecting-ransomware-precursors-in-network**](/docs/user-guide/skills/optional/security/security-detecting-ransomware-precursors-in-network) | Detects early-stage ransomware indicators in network |
| [**detecting-rdp-brute-force-attacks**](/docs/user-guide/skills/optional/security/security-detecting-rdp-brute-force-attacks) | Detect RDP brute force attacks by parsing Windows Security |
| [**detecting-rootkit-activity**](/docs/user-guide/skills/optional/security/security-detecting-rootkit-activity) | Detects rootkit presence on compromised systems by |
| [**detecting-s3-data-exfiltration-attempts**](/docs/user-guide/skills/optional/security/security-detecting-s3-data-exfiltration-attempts) | Detecting data exfiltration attempts from AWS S3 buckets by |
| [**detecting-secure-boot-bypass**](/docs/user-guide/skills/optional/security/security-detecting-secure-boot-bypass) | Detect UEFI Secure Boot bypasses and bootkits such as |
| [**detecting-serverless-function-injection**](/docs/user-guide/skills/optional/security/security-detecting-serverless-function-injection) | Detects and prevents code injection attacks targeting |
| [**detecting-service-account-abuse**](/docs/user-guide/skills/optional/security/security-detecting-service-account-abuse) | Detect abuse of service accounts by hunting for anomalous |
| [**detecting-shadow-api-endpoints**](/docs/user-guide/skills/optional/security/security-detecting-shadow-api-endpoints) | Discover and inventory shadow API endpoints that operate |
| [**detecting-shadow-it-cloud-usage**](/docs/user-guide/skills/optional/security/security-detecting-shadow-it-cloud-usage) | Detect unauthorized SaaS and cloud service usage (shadow |
| [**detecting-spearphishing-with-email-gateway**](/docs/user-guide/skills/optional/security/security-detecting-spearphishing-with-email-gateway) | Detect and block spearphishing emails that use |
| [**detecting-sql-injection-via-waf-logs**](/docs/user-guide/skills/optional/security/security-detecting-sql-injection-via-waf-logs) | Analyze WAF (ModSecurity/AWS WAF/Cloudflare) logs to detect |
| [**detecting-stuxnet-style-attacks**](/docs/user-guide/skills/optional/security/security-detecting-stuxnet-style-attacks) | Detects sophisticated cyber-physical attacks that follow |
| [**detecting-supply-chain-attacks-in-ci-cd**](/docs/user-guide/skills/optional/security/security-detecting-supply-chain-attacks-in-ci-cd) | Scans GitHub Actions workflows and CI/CD pipeline |
| [**detecting-suspicious-oauth-application-consent**](/docs/user-guide/skills/optional/security/security-detecting-suspicious-oauth-application-consent) | Detect risky OAuth application consent grants in Azure AD / |
| [**detecting-suspicious-powershell-execution**](/docs/user-guide/skills/optional/security/security-detecting-suspicious-powershell-execution) | Hunt for suspicious PowerShell execution (T1059.001) such |
| [**detecting-t1003-credential-dumping-with-edr**](/docs/user-guide/skills/optional/security/security-detecting-t1003-credential-dumping-with-edr) | Detect OS credential dumping (MITRE T1003) targeting LSASS |
| [**detecting-t1055-process-injection-with-sysmon**](/docs/user-guide/skills/optional/security/security-detecting-t1055-process-injection-with-sysmon) | Detect process injection techniques (T1055) - including DLL |
| [**detecting-t1548-abuse-elevation-control-mechanism**](/docs/user-guide/skills/optional/security/security-detecting-t1548-abuse-elevation-control-mechanism) | Detect abuse of elevation control mechanisms (T1548) |
| [**detecting-typosquatting-packages**](/docs/user-guide/skills/optional/security/security-detecting-typosquatting-packages) | Flag misspelled, brandjacked, and typosquatted package |
| [**detecting-typosquatting-packages-in-npm-pypi**](/docs/user-guide/skills/optional/security/security-detecting-typosquatting-packages-in-npm-pypi) | Detects typosquatting attacks in npm and PyPI package |
| [**detecting-wmi-persistence**](/docs/user-guide/skills/optional/security/security-detecting-wmi-persistence) | Detect WMI event subscription persistence (MITRE T1546.003) |
| [**emulating-cloud-attacks-with-stratus-red-team**](/docs/user-guide/skills/optional/security/security-emulating-cloud-attacks-with-stratus-red-team) | Install and run Stratus Red Team to detonate granular |
| [**enumerating-cloud-with-cloudfox**](/docs/user-guide/skills/optional/security/security-enumerating-cloud-with-cloudfox) | Run CloudFox's read-only Describe/List/Get enumeration |
| [**eradicating-malware-from-infected-systems**](/docs/user-guide/skills/optional/security/security-eradicating-malware-from-infected-systems) | Systematically map and remove malware, backdoors, and |
| [**escaping-containers-to-host**](/docs/user-guide/skills/optional/security/security-escaping-containers-to-host) | Exploits privileged pods, host mounts, runC CVEs, and |
| [**evaluating-threat-intelligence-platforms**](/docs/user-guide/skills/optional/security/security-evaluating-threat-intelligence-platforms) | Evaluates and selects Threat Intelligence Platform (TIP) |
| [**executing-nist-rmf-authorization-to-operate**](/docs/user-guide/skills/optional/security/security-executing-nist-rmf-authorization-to-operate) | Drive a federal system through the NIST Risk Management |
| [**exploiting-api-injection-vulnerabilities**](/docs/user-guide/skills/optional/security/security-exploiting-api-injection-vulnerabilities) | Tests API parameters, headers, and request bodies for |
| [**exploiting-aws-with-pacu**](/docs/user-guide/skills/optional/security/security-exploiting-aws-with-pacu) | Runs the Pacu AWS exploitation framework end-to-end — |
| [**exploiting-bgp-hijacking-vulnerabilities**](/docs/user-guide/skills/optional/security/security-exploiting-bgp-hijacking-vulnerabilities) | Analyzes and simulates BGP hijacking scenarios in |
| [**exploiting-broken-function-level-authorization**](/docs/user-guide/skills/optional/security/security-exploiting-broken-function-level-authorization) | Tests APIs for Broken Function Level Authorization (OWASP |
| [**exploiting-broken-link-hijacking**](/docs/user-guide/skills/optional/security/security-exploiting-broken-link-hijacking) | Discovers and exploits broken link hijacking by spidering a |
| [**exploiting-deeplink-vulnerabilities**](/docs/user-guide/skills/optional/security/security-exploiting-deeplink-vulnerabilities) | Tests and exploits deep link (URL scheme and App Link) |
| [**exploiting-excessive-data-exposure-in-api**](/docs/user-guide/skills/optional/security/security-exploiting-excessive-data-exposure-in-api) | Tests APIs for excessive data exposure (OWASP API3:2023) by |
| [**exploiting-http-request-smuggling**](/docs/user-guide/skills/optional/security/security-exploiting-http-request-smuggling) | Detects and exploits HTTP request smuggling caused by |
| [**exploiting-idor-vulnerabilities**](/docs/user-guide/skills/optional/security/security-exploiting-idor-vulnerabilities) | Identifies and exploits Insecure Direct Object Reference |
| [**exploiting-insecure-data-storage-in-mobile**](/docs/user-guide/skills/optional/security/security-exploiting-insecure-data-storage-in-mobile) | Identifies and exploits insecure local data storage |
| [**exploiting-insecure-deserialization**](/docs/user-guide/skills/optional/security/security-exploiting-insecure-deserialization) | Identifying and exploiting insecure deserialization |
| [**exploiting-ipv6-vulnerabilities**](/docs/user-guide/skills/optional/security/security-exploiting-ipv6-vulnerabilities) | Identifies and exploits IPv6-specific vulnerabilities |
| [**exploiting-jwt-algorithm-confusion-attack**](/docs/user-guide/skills/optional/security/security-exploiting-jwt-algorithm-confusion-attack) | Exploits JWT algorithm confusion where the server's |
| [**exploiting-mass-assignment-in-rest-apis**](/docs/user-guide/skills/optional/security/security-exploiting-mass-assignment-in-rest-apis) | Discovers and exploits mass assignment (autobinding) in |
| [**exploiting-nosql-injection-vulnerabilities**](/docs/user-guide/skills/optional/security/security-exploiting-nosql-injection-vulnerabilities) | Detects and exploits NoSQL injection vulnerabilities in |
| [**exploiting-oauth-misconfiguration**](/docs/user-guide/skills/optional/security/security-exploiting-oauth-misconfiguration) | Identifying and exploiting OAuth 2.0 and OpenID Connect |
| [**exploiting-prototype-pollution-in-javascript**](/docs/user-guide/skills/optional/security/security-exploiting-prototype-pollution-in-javascript) | Detects and exploits JavaScript prototype pollution |
| [**exploiting-race-condition-vulnerabilities**](/docs/user-guide/skills/optional/security/security-exploiting-race-condition-vulnerabilities) | Detects and exploits race condition (TOCTOU) |
| [**exploiting-server-side-request-forgery**](/docs/user-guide/skills/optional/security/security-exploiting-server-side-request-forgery) | Identifying and exploiting SSRF vulnerabilities to access |
| [**exploiting-smb-vulnerabilities-with-metasploit**](/docs/user-guide/skills/optional/security/security-exploiting-smb-vulnerabilities-with-metasploit) | Identifies and exploits SMB protocol vulnerabilities using |
| [**exploiting-sql-injection-with-sqlmap**](/docs/user-guide/skills/optional/security/security-exploiting-sql-injection-with-sqlmap) | Detecting and exploiting SQL injection vulnerabilities |
| [**exploiting-template-injection-vulnerabilities**](/docs/user-guide/skills/optional/security/security-exploiting-template-injection-vulnerabilities) | Detects and exploits Server-Side Template Injection (SSTI) |
| [**exploiting-type-juggling-vulnerabilities**](/docs/user-guide/skills/optional/security/security-exploiting-type-juggling-vulnerabilities) | Exploits PHP type juggling vulnerabilities caused by loose |
| [**exploiting-vulnerabilities-with-metasploit-framework**](/docs/user-guide/skills/optional/security/security-exploiting-vulnerabilities-with-metasploit-framework) | Uses the Metasploit Framework (msfconsole and its exploit |
| [**exploiting-websocket-vulnerabilities**](/docs/user-guide/skills/optional/security/security-exploiting-websocket-vulnerabilities) | Testing WebSocket implementations for authentication |
| [**extracting-browser-history-artifacts**](/docs/user-guide/skills/optional/security/security-extracting-browser-history-artifacts) | Extracts and analyzes browser history, cookies, cache |
| [**extracting-config-from-agent-tesla-rat**](/docs/user-guide/skills/optional/security/security-extracting-config-from-agent-tesla-rat) | Extracts embedded configuration from Agent Tesla RAT |
| [**extracting-credentials-from-memory-dump**](/docs/user-guide/skills/optional/security/security-extracting-credentials-from-memory-dump) | Extracts cached credentials, password hashes, Kerberos |
| [**extracting-iocs-from-malware-samples**](/docs/user-guide/skills/optional/security/security-extracting-iocs-from-malware-samples) | Extracts indicators of compromise (IOCs) from malware |
| [**extracting-memory-artifacts-with-rekall**](/docs/user-guide/skills/optional/security/security-extracting-memory-artifacts-with-rekall) | Uses Rekall memory forensics framework to analyze memory |
| [**extracting-windows-event-logs-artifacts**](/docs/user-guide/skills/optional/security/security-extracting-windows-event-logs-artifacts) | Extract, parse, and analyze Windows Event Logs (EVTX) using |
| [**fleet-hunting-with-velociraptor**](/docs/user-guide/skills/optional/security/security-fleet-hunting-with-velociraptor) | Deploy a Velociraptor server and agents, then author VQL |
| [**generating-and-analyzing-sboms**](/docs/user-guide/skills/optional/security/security-generating-and-analyzing-sboms) | Generate CycloneDX and SPDX SBOMs from container images and |
| [**generating-forensic-timelines-with-hayabusa**](/docs/user-guide/skills/optional/security/security-generating-forensic-timelines-with-hayabusa) | Run Hayabusa against collected Windows EVTX files to apply |
| [**generating-threat-intelligence-reports**](/docs/user-guide/skills/optional/security/security-generating-threat-intelligence-reports) | Generates structured cyber threat intelligence reports at |
| [**godmode**](/docs/user-guide/skills/optional/security/security-godmode) | Jailbreak LLMs: Parseltongue, GODMODE, ULTRAPLINIAN. |
| [**hardening-docker-containers-for-production**](/docs/user-guide/skills/optional/security/security-hardening-docker-containers-for-production) | Hardens Dockerfiles, images, and per-container runtime |
| [**hardening-docker-daemon-configuration**](/docs/user-guide/skills/optional/security/security-hardening-docker-daemon-configuration) | Hardens the Docker daemon (dockerd) through |
| [**hardening-linux-endpoint-with-cis-benchmark**](/docs/user-guide/skills/optional/security/security-hardening-linux-endpoint-with-cis-benchmark) | Hardens Linux endpoints using CIS Benchmark recommendations |
| [**hardening-windows-endpoint-with-cis-benchmark**](/docs/user-guide/skills/optional/security/security-hardening-windows-endpoint-with-cis-benchmark) | Hardens Windows endpoints using CIS (Center for Internet |
| [**hunting-advanced-persistent-threats**](/docs/user-guide/skills/optional/security/security-hunting-advanced-persistent-threats) | Proactively hunts for Advanced Persistent Threat (APT) |
| [**hunting-bootkits-in-efi-system-partition**](/docs/user-guide/skills/optional/security/security-hunting-bootkits-in-efi-system-partition) | Baseline the EFI System Partition and hunt malicious EFI |
| [**hunting-credential-stuffing-attacks**](/docs/user-guide/skills/optional/security/security-hunting-credential-stuffing-attacks) | Detects credential stuffing attacks by analyzing |
| [**hunting-evtx-with-chainsaw**](/docs/user-guide/skills/optional/security/security-hunting-evtx-with-chainsaw) | Run Chainsaw against collected Windows EVTX files to hunt |
| [**hunting-for-anomalous-powershell-execution**](/docs/user-guide/skills/optional/security/security-hunting-for-anomalous-powershell-execution) | Hunt for malicious PowerShell activity by analyzing Script |
| [**hunting-for-beaconing-with-frequency-analysis**](/docs/user-guide/skills/optional/security/security-hunting-for-beaconing-with-frequency-analysis) | Identify command-and-control beaconing patterns in network |
| [**hunting-for-cobalt-strike-beacons**](/docs/user-guide/skills/optional/security/security-hunting-for-cobalt-strike-beacons) | Detect Cobalt Strike beacon command-and-control traffic |
| [**hunting-for-command-and-control-beaconing**](/docs/user-guide/skills/optional/security/security-hunting-for-command-and-control-beaconing) | Detect C2 beaconing patterns in network traffic using |
| [**hunting-for-data-exfiltration-indicators**](/docs/user-guide/skills/optional/security/security-hunting-for-data-exfiltration-indicators) | Hunt for data exfiltration by analyzing Zeek and Suricata |
| [**hunting-for-data-staging-before-exfiltration**](/docs/user-guide/skills/optional/security/security-hunting-for-data-staging-before-exfiltration) | Detect data-staging activity (MITRE ATT&CK T1074) by |
| [**hunting-for-dcom-lateral-movement**](/docs/user-guide/skills/optional/security/security-hunting-for-dcom-lateral-movement) | Hunt for DCOM-based lateral movement (MITRE ATT&CK |
| [**hunting-for-dcsync-attacks**](/docs/user-guide/skills/optional/security/security-hunting-for-dcsync-attacks) | Detect DCSync attacks (MITRE ATT&CK T1003.006) by analyzing |
| [**hunting-for-defense-evasion-via-timestomping**](/docs/user-guide/skills/optional/security/security-hunting-for-defense-evasion-via-timestomping) | Detect NTFS timestamp manipulation (MITRE T1070.006) by |
| [**hunting-for-dns-based-persistence**](/docs/user-guide/skills/optional/security/security-hunting-for-dns-based-persistence) | Hunts for DNS-based persistence mechanisms such as DNS |
| [**hunting-for-dns-tunneling-with-zeek**](/docs/user-guide/skills/optional/security/security-hunting-for-dns-tunneling-with-zeek) | Detects DNS tunneling and covert-channel data exfiltration |
| [**hunting-for-domain-fronting-c2-traffic**](/docs/user-guide/skills/optional/security/security-hunting-for-domain-fronting-c2-traffic) | Detects domain fronting C2 traffic by analyzing |
| [**hunting-for-lateral-movement-via-wmi**](/docs/user-guide/skills/optional/security/security-hunting-for-lateral-movement-via-wmi) | Detects WMI-based lateral movement (e.g |
| [**hunting-for-living-off-the-cloud-techniques**](/docs/user-guide/skills/optional/security/security-hunting-for-living-off-the-cloud-techniques) | Hunts for adversary abuse of legitimate cloud services |
| [**hunting-for-living-off-the-land-binaries**](/docs/user-guide/skills/optional/security/security-hunting-for-living-off-the-land-binaries) | Proactively hunts for adversary abuse of legitimate, signed |
| [**hunting-for-lolbins-execution-in-endpoint-logs**](/docs/user-guide/skills/optional/security/security-hunting-for-lolbins-execution-in-endpoint-logs) | Hunts for LOLBins (Living Off the Land Binaries) abuse |
| [**hunting-for-ntlm-relay-attacks**](/docs/user-guide/skills/optional/security/security-hunting-for-ntlm-relay-attacks) | Detects NTLM relay attacks (MITRE T1557.001) by analyzing |
| [**hunting-for-persistence-mechanisms-in-windows**](/docs/user-guide/skills/optional/security/security-hunting-for-persistence-mechanisms-in-windows) | Systematically hunts for adversary persistence mechanisms |
| [**hunting-for-persistence-via-wmi-subscriptions**](/docs/user-guide/skills/optional/security/security-hunting-for-persistence-via-wmi-subscriptions) | Hunts for adversary persistence via WMI event subscriptions |
| [**hunting-for-process-injection-techniques**](/docs/user-guide/skills/optional/security/security-hunting-for-process-injection-techniques) | Detects process injection techniques (MITRE T1055) — |
| [**hunting-for-registry-persistence-mechanisms**](/docs/user-guide/skills/optional/security/security-hunting-for-registry-persistence-mechanisms) | Hunts for registry-based persistence mechanisms (MITRE |
| [**hunting-for-registry-run-key-persistence**](/docs/user-guide/skills/optional/security/security-hunting-for-registry-run-key-persistence) | Detect MITRE ATT&CK T1547.001 registry Run key persistence |
| [**hunting-for-scheduled-task-persistence**](/docs/user-guide/skills/optional/security/security-hunting-for-scheduled-task-persistence) | Runs a hypothesis-driven threat hunt for Windows Scheduled |
| [**hunting-for-shadow-copy-deletion**](/docs/user-guide/skills/optional/security/security-hunting-for-shadow-copy-deletion) | Runs a hypothesis-driven threat hunt for Volume Shadow Copy |
| [**hunting-for-spearphishing-indicators**](/docs/user-guide/skills/optional/security/security-hunting-for-spearphishing-indicators) | Hunt for spearphishing campaign indicators across email |
| [**hunting-for-startup-folder-persistence**](/docs/user-guide/skills/optional/security/security-hunting-for-startup-folder-persistence) | Detects T1547.001 startup folder persistence by monitoring |
| [**hunting-for-supply-chain-compromise**](/docs/user-guide/skills/optional/security/security-hunting-for-supply-chain-compromise) | Runs a hypothesis-driven threat hunt for supply-chain |
| [**hunting-for-suspicious-scheduled-tasks**](/docs/user-guide/skills/optional/security/security-hunting-for-suspicious-scheduled-tasks) | Hunts for adversary persistence and execution via Windows |
| [**hunting-for-t1098-account-manipulation**](/docs/user-guide/skills/optional/security/security-hunting-for-t1098-account-manipulation) | Hunts for MITRE ATT&CK T1098 account manipulation - shadow |
| [**hunting-for-unusual-network-connections**](/docs/user-guide/skills/optional/security/security-hunting-for-unusual-network-connections) | Runs a hypothesis-driven threat hunt for |
| [**hunting-for-unusual-service-installations**](/docs/user-guide/skills/optional/security/security-hunting-for-unusual-service-installations) | Detects suspicious Windows service installations (MITRE |
| [**hunting-for-webshell-activity**](/docs/user-guide/skills/optional/security/security-hunting-for-webshell-activity) | Runs a hypothesis-driven threat hunt for web shell |
| [**hunting-saas-sso-token-abuse**](/docs/user-guide/skills/optional/security/security-hunting-saas-sso-token-abuse) | Hunts for stolen-session and OAuth/PRT token replay |
| [**implementing-aes-encryption-for-data-at-rest**](/docs/user-guide/skills/optional/security/security-implementing-aes-encryption-for-data-at-rest) | Guides implementing AES-256 encryption in GCM mode (FIPS |
| [**implementing-alert-fatigue-reduction**](/docs/user-guide/skills/optional/security/security-implementing-alert-fatigue-reduction) | Implements strategies to reduce SOC alert fatigue by tuning |
| [**implementing-anti-phishing-training-program**](/docs/user-guide/skills/optional/security/security-implementing-anti-phishing-training-program) | Guides designing, deploying, and measuring an anti-phishing |
| [**implementing-anti-ransomware-group-policy**](/docs/user-guide/skills/optional/security/security-implementing-anti-ransomware-group-policy) | Configures Windows Group Policy Objects to block ransomware |
| [**implementing-api-abuse-detection-with-rate-limiting**](/docs/user-guide/skills/optional/security/security-implementing-api-abuse-detection-with-rate-limiting) | Implements API abuse detection using token bucket, sliding |
| [**implementing-api-gateway-security-controls**](/docs/user-guide/skills/optional/security/security-implementing-api-gateway-security-controls) | Configures API gateways such as Kong, AWS API Gateway |
| [**implementing-api-key-security-controls**](/docs/user-guide/skills/optional/security/security-implementing-api-key-security-controls) | Implements secure API key generation with sufficient |
| [**implementing-api-rate-limiting-and-throttling**](/docs/user-guide/skills/optional/security/security-implementing-api-rate-limiting-and-throttling) | Implements API rate limiting and throttling with token |
| [**implementing-api-schema-validation-security**](/docs/user-guide/skills/optional/security/security-implementing-api-schema-validation-security) | Implements API schema validation using OpenAPI |
| [**implementing-api-security-posture-management**](/docs/user-guide/skills/optional/security/security-implementing-api-security-posture-management) | Implements API Security Posture Management (API-SPM) to |
| [**implementing-api-security-testing-with-42crunch**](/docs/user-guide/skills/optional/security/security-implementing-api-security-testing-with-42crunch) | Implements API security testing on the 42Crunch platform |
| [**implementing-api-threat-protection-with-apigee**](/docs/user-guide/skills/optional/security/security-implementing-api-threat-protection-with-apigee) | Implements API threat protection using Google Apigee |
| [**implementing-application-whitelisting-with-applocker**](/docs/user-guide/skills/optional/security/security-implementing-application-whitelisting-with-applocker) | Implements application whitelisting using Windows AppLocker |
| [**implementing-aqua-security-for-container-scanning**](/docs/user-guide/skills/optional/security/security-implementing-aqua-security-for-container-scanning) | Deploy Aqua Security's Trivy scanner to detect |
| [**implementing-attack-path-analysis-with-xm-cyber**](/docs/user-guide/skills/optional/security/security-implementing-attack-path-analysis-with-xm-cyber) | Deploys XM Cyber's continuous exposure management platform |
| [**implementing-aws-config-rules-for-compliance**](/docs/user-guide/skills/optional/security/security-implementing-aws-config-rules-for-compliance) | Implements AWS Config managed and custom rules for |
| [**implementing-aws-iam-permission-boundaries**](/docs/user-guide/skills/optional/security/security-implementing-aws-iam-permission-boundaries) | Configures AWS IAM permission boundaries that cap the |
| [**implementing-aws-macie-for-data-classification**](/docs/user-guide/skills/optional/security/security-implementing-aws-macie-for-data-classification) | Enable and configure Amazon Macie via AWS CLI/Terraform to |
| [**implementing-aws-nitro-enclave-security**](/docs/user-guide/skills/optional/security/security-implementing-aws-nitro-enclave-security) | Build AWS Nitro Enclave confidential computing environments |
| [**implementing-aws-security-hub**](/docs/user-guide/skills/optional/security/security-implementing-aws-security-hub) | Deploy AWS Security Hub as a centralized CSPM platform |
| [**implementing-aws-security-hub-compliance**](/docs/user-guide/skills/optional/security/security-implementing-aws-security-hub-compliance) | Deploy AWS Security Hub, backed by AWS Config, to aggregate |
| [**implementing-azure-ad-privileged-identity-management**](/docs/user-guide/skills/optional/security/security-implementing-azure-ad-privileged-identity-management) | Configure Microsoft Entra Privileged Identity Management |
| [**implementing-azure-defender-for-cloud**](/docs/user-guide/skills/optional/security/security-implementing-azure-defender-for-cloud) | Enable Microsoft Defender for Cloud (CSPM + CWPP) across |
| [**implementing-beyondcorp-zero-trust-access-model**](/docs/user-guide/skills/optional/security/security-implementing-beyondcorp-zero-trust-access-model) | Implement Google's BeyondCorp zero trust access model using |
| [**implementing-bgp-security-with-rpki**](/docs/user-guide/skills/optional/security/security-implementing-bgp-security-with-rpki) | Implement RPKI-based BGP route origin validation by |
| [**implementing-browser-isolation-for-zero-trust**](/docs/user-guide/skills/optional/security/security-implementing-browser-isolation-for-zero-trust) | Deploys remote browser isolation (RBI) as a core component |
| [**implementing-canary-tokens-for-network-intrusion**](/docs/user-guide/skills/optional/security/security-implementing-canary-tokens-for-network-intrusion) | Deploys DNS, HTTP, and AWS API key canary tokens across |
| [**implementing-cisa-zero-trust-maturity-model**](/docs/user-guide/skills/optional/security/security-implementing-cisa-zero-trust-maturity-model) | Assess, gap-analyze, and progressively implement the CISA |
| [**implementing-cloud-dlp-for-data-protection**](/docs/user-guide/skills/optional/security/security-implementing-cloud-dlp-for-data-protection) | Implement cloud DLP using Amazon Macie, Google Cloud DLP |
| [**implementing-cloud-security-posture-management**](/docs/user-guide/skills/optional/security/security-implementing-cloud-security-posture-management) | Continuously monitor multi-cloud environments (AWS, Azure |
| [**implementing-cloud-trail-log-analysis**](/docs/user-guide/skills/optional/security/security-implementing-cloud-trail-log-analysis) | Implementing AWS CloudTrail log analysis for security |
| [**implementing-cloud-vulnerability-posture-management**](/docs/user-guide/skills/optional/security/security-implementing-cloud-vulnerability-posture-management) | Implement multi-cloud CSPM to detect cloud-native |
| [**implementing-cloud-waf-rules**](/docs/user-guide/skills/optional/security/security-implementing-cloud-waf-rules) | Deploys and tunes Web Application Firewall rules on AWS |
| [**implementing-cloud-workload-protection**](/docs/user-guide/skills/optional/security/security-implementing-cloud-workload-protection) | Implements cloud workload protection using boto3 and |
| [**implementing-code-signing-for-artifacts**](/docs/user-guide/skills/optional/security/security-implementing-code-signing-for-artifacts) | Implements code signing for build artifacts (binaries |
| [**implementing-conditional-access-policies-azure-ad**](/docs/user-guide/skills/optional/security/security-implementing-conditional-access-policies-azure-ad) | Configures Microsoft Entra ID (Azure AD) Conditional Access |
| [**implementing-conduit-security-for-ot-remote-access**](/docs/user-guide/skills/optional/security/security-implementing-conduit-security-for-ot-remote-access) | Implements secure conduit architecture for OT remote access |
| [**implementing-container-image-minimal-base-with-distroless**](/docs/user-guide/skills/optional/security/security-implementing-container-image-minimal-base-with-distroless) | Reduces container attack surface by building application |
| [**implementing-container-network-policies-with-calico**](/docs/user-guide/skills/optional/security/security-implementing-container-network-policies-with-calico) | Uses Calico's own policy CRDs beyond the upstream |
| [**implementing-continuous-security-validation-with-bas**](/docs/user-guide/skills/optional/security/security-implementing-continuous-security-validation-with-bas) | Deploys Breach and Attack Simulation (BAS) platforms such |
| [**implementing-data-loss-prevention-with-microsoft-purview**](/docs/user-guide/skills/optional/security/security-implementing-data-loss-prevention-with-microsoft-purview) | Implements DLP policies using Microsoft Purview PowerShell |
| [**implementing-ddos-mitigation-with-cloudflare**](/docs/user-guide/skills/optional/security/security-implementing-ddos-mitigation-with-cloudflare) | Configure Cloudflare DDoS protection with managed rulesets |
| [**implementing-deception-based-detection-with-canarytoken**](/docs/user-guide/skills/optional/security/security-implementing-deception-based-detection-with-canarytoken) | Deploys and monitors Canary Tokens via the Thinkst Canary |
| [**implementing-delinea-secret-server-for-pam**](/docs/user-guide/skills/optional/security/security-implementing-delinea-secret-server-for-pam) | Implements Delinea Secret Server for privileged access |
| [**implementing-device-posture-assessment-in-zero-trust**](/docs/user-guide/skills/optional/security/security-implementing-device-posture-assessment-in-zero-trust) | Implements device posture assessment as a zero trust access |
| [**implementing-devsecops-security-scanning**](/docs/user-guide/skills/optional/security/security-implementing-devsecops-security-scanning) | Integrates SAST, DAST, and SCA into CI/CD pipelines using |
| [**implementing-diamond-model-analysis**](/docs/user-guide/skills/optional/security/security-implementing-diamond-model-analysis) | The Diamond Model of Intrusion Analysis provides a |
| [**implementing-digital-signatures-with-ed25519**](/docs/user-guide/skills/optional/security/security-implementing-digital-signatures-with-ed25519) | Implements digital signatures using the Ed25519 algorithm |
| [**implementing-disk-encryption-with-bitlocker**](/docs/user-guide/skills/optional/security/security-implementing-disk-encryption-with-bitlocker) | Implements full disk encryption using Microsoft BitLocker |
| [**implementing-dmarc-dkim-spf-email-security**](/docs/user-guide/skills/optional/security/security-implementing-dmarc-dkim-spf-email-security) | Configures SPF, DKIM, and DMARC DNS TXT records to |
| [**implementing-dragos-platform-for-ot-monitoring**](/docs/user-guide/skills/optional/security/security-implementing-dragos-platform-for-ot-monitoring) | Deploys and configures Dragos Platform sensors and |
| [**implementing-ebpf-security-monitoring**](/docs/user-guide/skills/optional/security/security-implementing-ebpf-security-monitoring) | Implements eBPF-based security monitoring using Cilium |
| [**implementing-email-sandboxing-with-proofpoint**](/docs/user-guide/skills/optional/security/security-implementing-email-sandboxing-with-proofpoint) | Email sandboxing detonates suspicious attachments and URLs |
| [**implementing-end-to-end-encryption-for-messaging**](/docs/user-guide/skills/optional/security/security-implementing-end-to-end-encryption-for-messaging) | Implements a simplified Signal Protocol-style end-to-end |
| [**implementing-endpoint-detection-with-wazuh**](/docs/user-guide/skills/optional/security/security-implementing-endpoint-detection-with-wazuh) | Deploys and configures Wazuh SIEM/XDR for endpoint |
| [**implementing-endpoint-dlp-controls**](/docs/user-guide/skills/optional/security/security-implementing-endpoint-dlp-controls) | Implements endpoint Data Loss Prevention (DLP) controls to |
| [**implementing-envelope-encryption-with-aws-kms**](/docs/user-guide/skills/optional/security/security-implementing-envelope-encryption-with-aws-kms) | Implements envelope encryption with AWS KMS, encrypting |
| [**implementing-epss-score-for-vulnerability-prioritization**](/docs/user-guide/skills/optional/security/security-implementing-epss-score-for-vulnerability-prioritization) | Queries FIRST's Exploit Prediction Scoring System (EPSS) |
| [**implementing-file-integrity-monitoring-with-aide**](/docs/user-guide/skills/optional/security/security-implementing-file-integrity-monitoring-with-aide) | Configures AIDE (Advanced Intrusion Detection Environment) |
| [**implementing-fuzz-testing-in-cicd-with-aflplusplus**](/docs/user-guide/skills/optional/security/security-implementing-fuzz-testing-in-cicd-with-aflplusplus) | Integrates AFL++ coverage-guided fuzzing into CI/CD |
| [**implementing-gcp-binary-authorization**](/docs/user-guide/skills/optional/security/security-implementing-gcp-binary-authorization) | Implements GCP Binary Authorization end to end, including |
| [**implementing-gcp-organization-policy-constraints**](/docs/user-guide/skills/optional/security/security-implementing-gcp-organization-policy-constraints) | Implements GCP Organization Policy constraints via gcloud |
| [**implementing-gcp-vpc-firewall-rules**](/docs/user-guide/skills/optional/security/security-implementing-gcp-vpc-firewall-rules) | Implements and audits GCP VPC firewall rules using gcloud |
| [**implementing-gdpr-data-protection-controls**](/docs/user-guide/skills/optional/security/security-implementing-gdpr-data-protection-controls) | Implements GDPR (EU 2016/679) technical and organizational |
| [**implementing-gdpr-data-subject-access-request**](/docs/user-guide/skills/optional/security/security-implementing-gdpr-data-subject-access-request) | Automates GDPR Data Subject Access Request (DSAR) workflows |
| [**implementing-github-advanced-security-for-code-scanning**](/docs/user-guide/skills/optional/security/security-implementing-github-advanced-security-for-code-scanning) | Configures GitHub Advanced Security (code scanning with |
| [**implementing-google-workspace-admin-security**](/docs/user-guide/skills/optional/security/security-implementing-google-workspace-admin-security) | Hardens a Google Workspace tenant via Admin Console |
| [**implementing-google-workspace-phishing-protection**](/docs/user-guide/skills/optional/security/security-implementing-google-workspace-phishing-protection) | Configures Google Workspace advanced phishing and malware |
| [**implementing-google-workspace-sso-configuration**](/docs/user-guide/skills/optional/security/security-implementing-google-workspace-sso-configuration) | Configures SAML 2.0 single sign-on for Google Workspace |
| [**implementing-hardware-security-key-authentication**](/docs/user-guide/skills/optional/security/security-implementing-hardware-security-key-authentication) | Builds a FIDO2/WebAuthn relying party server with the |
| [**implementing-hashicorp-vault-dynamic-secrets**](/docs/user-guide/skills/optional/security/security-implementing-hashicorp-vault-dynamic-secrets) | Configures HashiCorp Vault dynamic secrets engines for |
| [**implementing-hipaa-security-rule-safeguards**](/docs/user-guide/skills/optional/security/security-implementing-hipaa-security-rule-safeguards) | Implement the HIPAA Security Rule (45 CFR Part 164 Subpart |
| [**implementing-honeypot-for-ransomware-detection**](/docs/user-guide/skills/optional/security/security-implementing-honeypot-for-ransomware-detection) | Deploys canary files, honeypot shares, and decoy systems to |
| [**implementing-honeytokens-for-breach-detection**](/docs/user-guide/skills/optional/security/security-implementing-honeytokens-for-breach-detection) | Deploys canary tokens and honeytokens (fake AWS |
| [**implementing-ics-firewall-with-tofino**](/docs/user-guide/skills/optional/security/security-implementing-ics-firewall-with-tofino) | Deploys and configures Tofino industrial firewalls |
| [**implementing-identity-governance-with-sailpoint**](/docs/user-guide/skills/optional/security/security-implementing-identity-governance-with-sailpoint) | Deploys SailPoint IdentityNow or IdentityIQ for identity |
| [**implementing-identity-verification-for-zero-trust**](/docs/user-guide/skills/optional/security/security-implementing-identity-verification-for-zero-trust) | Implements continuous, risk-adaptive identity verification |
| [**implementing-iec-62443-security-zones**](/docs/user-guide/skills/optional/security/security-implementing-iec-62443-security-zones) | Designs security zones and conduits for industrial control |
| [**implementing-image-provenance-verification-with-cosign**](/docs/user-guide/skills/optional/security/security-implementing-image-provenance-verification-with-cosign) | Signs and verifies container image provenance with Sigstore |
| [**implementing-immutable-backup-with-restic**](/docs/user-guide/skills/optional/security/security-implementing-immutable-backup-with-restic) | Implements ransomware-resistant backups using restic with |
| [**implementing-infrastructure-as-code-security-scanning**](/docs/user-guide/skills/optional/security/security-implementing-infrastructure-as-code-security-scanning) | Implements automated security scanning for Infrastructure |
| [**implementing-iso-27001-information-security-management**](/docs/user-guide/skills/optional/security/security-implementing-iso-27001-information-security-management) | Guides implementation of an ISO/IEC 27001:2022 Information |
| [**implementing-just-in-time-access-provisioning**](/docs/user-guide/skills/optional/security/security-implementing-just-in-time-access-provisioning) | Implements Just-In-Time (JIT) access provisioning to |
| [**implementing-jwt-signing-and-verification**](/docs/user-guide/skills/optional/security/security-implementing-jwt-signing-and-verification) | Implements secure JWT (RFC 7519) signing and verification |
| [**implementing-kubernetes-network-policy-with-calico**](/docs/user-guide/skills/optional/security/security-implementing-kubernetes-network-policy-with-calico) | Installs Calico as the cluster CNI and writes standard |
| [**implementing-kubernetes-pod-security-standards**](/docs/user-guide/skills/optional/security/security-implementing-kubernetes-pod-security-standards) | Chooses and applies the correct Kubernetes Pod Security |
| [**implementing-llm-guardrails-for-security**](/docs/user-guide/skills/optional/security/security-implementing-llm-guardrails-for-security) | Implements input/output validation guardrails for LLM |
| [**implementing-log-forwarding-with-fluentd**](/docs/user-guide/skills/optional/security/security-implementing-log-forwarding-with-fluentd) | Configures Fluent Bit as an endpoint log forwarder and |
| [**implementing-log-integrity-with-blockchain**](/docs/user-guide/skills/optional/security/security-implementing-log-integrity-with-blockchain) | Builds an append-only log integrity chain using SHA-256 |
| [**implementing-memory-protection-with-dep-aslr**](/docs/user-guide/skills/optional/security/security-implementing-memory-protection-with-dep-aslr) | Implements memory protection mechanisms including DEP (Data |
| [**implementing-microsegmentation-with-guardicore**](/docs/user-guide/skills/optional/security/security-implementing-microsegmentation-with-guardicore) | Implements microsegmentation with Akamai Guardicore |
| [**implementing-mimecast-targeted-attack-protection**](/docs/user-guide/skills/optional/security/security-implementing-mimecast-targeted-attack-protection) | Deploys and configures Mimecast Targeted Threat Protection |
| [**implementing-mitre-attack-coverage-mapping**](/docs/user-guide/skills/optional/security/security-implementing-mitre-attack-coverage-mapping) | Implement MITRE ATT&CK coverage mapping to identify |
| [**implementing-mobile-application-management**](/docs/user-guide/skills/optional/security/security-implementing-mobile-application-management) | Implements Mobile Application Management (MAM) policies to |
| [**implementing-mtls-for-zero-trust-services**](/docs/user-guide/skills/optional/security/security-implementing-mtls-for-zero-trust-services) | Configures mutual TLS (mTLS) authentication between |
| [**implementing-nerc-cip-compliance-controls**](/docs/user-guide/skills/optional/security/security-implementing-nerc-cip-compliance-controls) | Implements NERC CIP controls for Bulk Electric System (BES) |
| [**implementing-network-access-control**](/docs/user-guide/skills/optional/security/security-implementing-network-access-control) | Implements 802.1X port-based network access control using |
| [**implementing-network-access-control-with-cisco-ise**](/docs/user-guide/skills/optional/security/security-implementing-network-access-control-with-cisco-ise) | Deploys Cisco Identity Services Engine (ISE) as a RADIUS |
| [**implementing-network-deception-with-honeypots**](/docs/user-guide/skills/optional/security/security-implementing-network-deception-with-honeypots) | Deploy and manage network honeypots using OpenCanary |
| [**implementing-network-intrusion-prevention-with-suricata**](/docs/user-guide/skills/optional/security/security-implementing-network-intrusion-prevention-with-suricata) | Deploys and configures Suricata as an inline network |
| [**implementing-network-policies-for-kubernetes**](/docs/user-guide/skills/optional/security/security-implementing-network-policies-for-kubernetes) | Writes portable upstream Kubernetes NetworkPolicy YAML - |
| [**implementing-network-segmentation-for-ot**](/docs/user-guide/skills/optional/security/security-implementing-network-segmentation-for-ot) | Implements OT network segmentation using VLANs, OT-aware |
| [**implementing-network-segmentation-with-firewall-zones**](/docs/user-guide/skills/optional/security/security-implementing-network-segmentation-with-firewall-zones) | Designs and implements network segmentation using firewall |
| [**implementing-network-traffic-analysis-with-arkime**](/docs/user-guide/skills/optional/security/security-implementing-network-traffic-analysis-with-arkime) | Queries Arkime (formerly Moloch) full packet capture via |
| [**implementing-network-traffic-baselining**](/docs/user-guide/skills/optional/security/security-implementing-network-traffic-baselining) | Builds network traffic baselines from NetFlow/IPFIX CSV or |
| [**implementing-next-generation-firewall-with-palo-alto**](/docs/user-guide/skills/optional/security/security-implementing-next-generation-firewall-with-palo-alto) | Configures and deploys Palo Alto Networks next-generation |
| [**implementing-opa-gatekeeper-for-policy-enforcement**](/docs/user-guide/skills/optional/security/security-implementing-opa-gatekeeper-for-policy-enforcement) | Deploys OPA Gatekeeper via Helm as a Kubernetes admission |
| [**implementing-ot-incident-response-playbook**](/docs/user-guide/skills/optional/security/security-implementing-ot-incident-response-playbook) | Develops OT-specific incident response playbooks using a |
| [**implementing-ot-network-traffic-analysis-with-nozomi**](/docs/user-guide/skills/optional/security/security-implementing-ot-network-traffic-analysis-with-nozomi) | Deploy Nozomi Networks Guardian sensors for passive OT |
| [**implementing-pam-for-database-access**](/docs/user-guide/skills/optional/security/security-implementing-pam-for-database-access) | Deploy privileged access management for database systems |
| [**implementing-passwordless-auth-with-microsoft-entra**](/docs/user-guide/skills/optional/security/security-implementing-passwordless-auth-with-microsoft-entra) | Implements passwordless authentication using Microsoft |
| [**implementing-passwordless-authentication-with-fido2**](/docs/user-guide/skills/optional/security/security-implementing-passwordless-authentication-with-fido2) | Deploy FIDO2/WebAuthn passwordless authentication using |
| [**implementing-patch-management-for-ot-systems**](/docs/user-guide/skills/optional/security/security-implementing-patch-management-for-ot-systems) | Implements a structured patch management program for OT/ICS |
| [**implementing-patch-management-workflow**](/docs/user-guide/skills/optional/security/security-implementing-patch-management-workflow) | Patch management is the systematic process of identifying |
| [**implementing-pci-dss-compliance-controls**](/docs/user-guide/skills/optional/security/security-implementing-pci-dss-compliance-controls) | Implements PCI DSS 4.0.1's 12 requirements across 6 control |
| [**implementing-pod-security-admission-controller**](/docs/user-guide/skills/optional/security/security-implementing-pod-security-admission-controller) | Configures and operates the Kubernetes Pod Security |
| [**implementing-policy-as-code-with-open-policy-agent**](/docs/user-guide/skills/optional/security/security-implementing-policy-as-code-with-open-policy-agent) | Implements policy-as-code enforcement with Open Policy |
| [**implementing-privileged-access-management-with-cyberark**](/docs/user-guide/skills/optional/security/security-implementing-privileged-access-management-with-cyberark) | Deploy CyberArk Privileged Access Management to discover |
| [**implementing-privileged-access-workstation**](/docs/user-guide/skills/optional/security/security-implementing-privileged-access-workstation) | Design and implement Privileged Access Workstations (PAWs) |
| [**implementing-privileged-session-monitoring**](/docs/user-guide/skills/optional/security/security-implementing-privileged-session-monitoring) | Implements privileged session monitoring and recording |
| [**implementing-proofpoint-email-security-gateway**](/docs/user-guide/skills/optional/security/security-implementing-proofpoint-email-security-gateway) | Deploy and configure Proofpoint Email Protection as a |
| [**implementing-purdue-model-network-segmentation**](/docs/user-guide/skills/optional/security/security-implementing-purdue-model-network-segmentation) | Implement network segmentation based on the Purdue |
| [**implementing-ransomware-backup-strategy**](/docs/user-guide/skills/optional/security/security-implementing-ransomware-backup-strategy) | Designs a ransomware-resilient backup strategy using the |
| [**implementing-ransomware-kill-switch-detection**](/docs/user-guide/skills/optional/security/security-implementing-ransomware-kill-switch-detection) | Analyzes ransomware kill switch mechanisms, including |
| [**implementing-rapid7-insightvm-for-scanning**](/docs/user-guide/skills/optional/security/security-implementing-rapid7-insightvm-for-scanning) | Deploy and configure Rapid7 InsightVM Security Console and |
| [**implementing-rbac-hardening-for-kubernetes**](/docs/user-guide/skills/optional/security/security-implementing-rbac-hardening-for-kubernetes) | Hardens Kubernetes RBAC by designing least-privilege Roles |
| [**implementing-rsa-key-pair-management**](/docs/user-guide/skills/optional/security/security-implementing-rsa-key-pair-management) | Generates, stores, rotates, and manages RSA key pairs |
| [**implementing-runtime-application-self-protection**](/docs/user-guide/skills/optional/security/security-implementing-runtime-application-self-protection) | Deploy Runtime Application Self-Protection (RASP) agents to |
| [**implementing-runtime-security-with-tetragon**](/docs/user-guide/skills/optional/security/security-implementing-runtime-security-with-tetragon) | Implements eBPF-based runtime observability and in-kernel |
| [**implementing-saml-sso-with-okta**](/docs/user-guide/skills/optional/security/security-implementing-saml-sso-with-okta) | Implement SAML 2.0 Single Sign-On using Okta as the |
| [**implementing-scim-provisioning-with-okta**](/docs/user-guide/skills/optional/security/security-implementing-scim-provisioning-with-okta) | Implement automated user lifecycle provisioning and |
| [**implementing-secret-scanning-with-gitleaks**](/docs/user-guide/skills/optional/security/security-implementing-secret-scanning-with-gitleaks) | This skill covers implementing Gitleaks for detecting and |
| [**implementing-secrets-management-with-vault**](/docs/user-guide/skills/optional/security/security-implementing-secrets-management-with-vault) | Deploy HashiCorp Vault for centralized secrets management |
| [**implementing-secrets-scanning-in-ci-cd**](/docs/user-guide/skills/optional/security/security-implementing-secrets-scanning-in-ci-cd) | Integrate gitleaks and trufflehog into CI/CD pipelines to |
| [**implementing-security-chaos-engineering**](/docs/user-guide/skills/optional/security/security-implementing-security-chaos-engineering) | Implements security chaos engineering experiments that |
| [**implementing-security-information-sharing-with-stix2**](/docs/user-guide/skills/optional/security/security-implementing-security-information-sharing-with-stix2) | Create, validate, and share STIX 2.1 threat intelligence |
| [**implementing-security-monitoring-with-datadog**](/docs/user-guide/skills/optional/security/security-implementing-security-monitoring-with-datadog) | Implements security monitoring using Datadog Cloud SIEM |
| [**implementing-semgrep-for-custom-sast-rules**](/docs/user-guide/skills/optional/security/security-implementing-semgrep-for-custom-sast-rules) | Write custom Semgrep SAST rules in YAML to detect |
| [**implementing-siem-correlation-rules-for-apt**](/docs/user-guide/skills/optional/security/security-implementing-siem-correlation-rules-for-apt) | Write multi-event correlation rules in Splunk SPL and Sigma |
| [**implementing-siem-use-case-tuning**](/docs/user-guide/skills/optional/security/security-implementing-siem-use-case-tuning) | Tune SIEM detection rules in Splunk and Elastic to reduce |
| [**implementing-siem-use-cases-for-detection**](/docs/user-guide/skills/optional/security/security-implementing-siem-use-cases-for-detection) | Implements SIEM detection use cases by designing |
| [**implementing-sigstore-for-software-signing**](/docs/user-guide/skills/optional/security/security-implementing-sigstore-for-software-signing) | Implements Sigstore-based software signing and verification |
| [**implementing-soar-automation-with-phantom**](/docs/user-guide/skills/optional/security/security-implementing-soar-automation-with-phantom) | Implements Security Orchestration, Automation, and Response |
| [**implementing-soar-playbook-for-phishing**](/docs/user-guide/skills/optional/security/security-implementing-soar-playbook-for-phishing) | Automates phishing incident response by calling the Splunk |
| [**implementing-soar-playbook-with-palo-alto-xsoar**](/docs/user-guide/skills/optional/security/security-implementing-soar-playbook-with-palo-alto-xsoar) | Build automated incident response playbooks in Cortex XSOAR |
| [**implementing-stix-taxii-feed-integration**](/docs/user-guide/skills/optional/security/security-implementing-stix-taxii-feed-integration) | Implements a STIX 2.1/TAXII 2.1 threat-intelligence feed |
| [**implementing-supply-chain-security-with-in-toto**](/docs/user-guide/skills/optional/security/security-implementing-supply-chain-security-with-in-toto) | Implements supply chain integrity verification for |
| [**implementing-syslog-centralization-with-rsyslog**](/docs/user-guide/skills/optional/security/security-implementing-syslog-centralization-with-rsyslog) | Configure rsyslog for centralized log collection with TLS |
| [**implementing-taxii-server-with-opentaxii**](/docs/user-guide/skills/optional/security/security-implementing-taxii-server-with-opentaxii) | Deploy and configure a TAXII 2.1 server (Medallion) with |
| [**implementing-threat-intelligence-lifecycle-management**](/docs/user-guide/skills/optional/security/security-implementing-threat-intelligence-lifecycle-management) | Build out a full CTI program around the six-phase threat |
| [**implementing-threat-modeling-with-mitre-attack**](/docs/user-guide/skills/optional/security/security-implementing-threat-modeling-with-mitre-attack) | Implements threat modeling using the MITRE ATT&CK framework |
| [**implementing-ticketing-system-for-incidents**](/docs/user-guide/skills/optional/security/security-implementing-ticketing-system-for-incidents) | Implements an integrated incident ticketing system |
| [**implementing-usb-device-control-policy**](/docs/user-guide/skills/optional/security/security-implementing-usb-device-control-policy) | Implements USB device control policies to restrict |
| [**implementing-velociraptor-for-ir-collection**](/docs/user-guide/skills/optional/security/security-implementing-velociraptor-for-ir-collection) | Deploy and configure Velociraptor for scalable endpoint |
| [**implementing-vulnerability-management-with-greenbone**](/docs/user-guide/skills/optional/security/security-implementing-vulnerability-management-with-greenbone) | Deploy and operate Greenbone/OpenVAS vulnerability |
| [**implementing-vulnerability-remediation-sla**](/docs/user-guide/skills/optional/security/security-implementing-vulnerability-remediation-sla) | Design a vulnerability remediation SLA program covering |
| [**implementing-vulnerability-sla-breach-alerting**](/docs/user-guide/skills/optional/security/security-implementing-vulnerability-sla-breach-alerting) | Build an automated SLA breach alerting system for |
| [**implementing-web-application-logging-with-modsecurity**](/docs/user-guide/skills/optional/security/security-implementing-web-application-logging-with-modsecurity) | Configure ModSecurity WAF with the OWASP Core Rule Set |
| [**implementing-zero-knowledge-proof-for-authentication**](/docs/user-guide/skills/optional/security/security-implementing-zero-knowledge-proof-for-authentication) | Implements the Schnorr identification protocol and a |
| [**implementing-zero-standing-privilege-with-cyberark**](/docs/user-guide/skills/optional/security/security-implementing-zero-standing-privilege-with-cyberark) | Deploy CyberArk Secure Cloud Access (SCA) to eliminate |
| [**implementing-zero-trust-dns-with-nextdns**](/docs/user-guide/skills/optional/security/security-implementing-zero-trust-dns-with-nextdns) | Configure NextDNS as an encrypted (DoH/DoT) zero trust DNS |
| [**implementing-zero-trust-for-saas-applications**](/docs/user-guide/skills/optional/security/security-implementing-zero-trust-for-saas-applications) | Secures SaaS apps (Microsoft 365, Google Workspace |
| [**implementing-zero-trust-in-cloud**](/docs/user-guide/skills/optional/security/security-implementing-zero-trust-in-cloud) | Guides zero trust implementation across AWS, Azure, and GCP |
| [**implementing-zero-trust-network-access**](/docs/user-guide/skills/optional/security/security-implementing-zero-trust-network-access) | Configures Zero Trust Network Access (ZTNA) in AWS, Azure |
| [**implementing-zero-trust-network-access-with-zscaler**](/docs/user-guide/skills/optional/security/security-implementing-zero-trust-network-access-with-zscaler) | Configures Zero Trust Network Access using Zscaler Private |
| [**implementing-zero-trust-with-beyondcorp**](/docs/user-guide/skills/optional/security/security-implementing-zero-trust-with-beyondcorp) | Configures Google BeyondCorp Enterprise Identity-Aware |
| [**implementing-zero-trust-with-hashicorp-boundary**](/docs/user-guide/skills/optional/security/security-implementing-zero-trust-with-hashicorp-boundary) | Installs and configures HashiCorp Boundary as a |
| [**integrating-dast-with-owasp-zap-in-pipeline**](/docs/user-guide/skills/optional/security/security-integrating-dast-with-owasp-zap-in-pipeline) | Integrates OWASP ZAP (Zed Attack Proxy) into GitHub Actions |
| [**integrating-sast-into-github-actions-pipeline**](/docs/user-guide/skills/optional/security/security-integrating-sast-into-github-actions-pipeline) | Integrates CodeQL and Semgrep SAST scanning into GitHub |
| [**intercepting-mobile-traffic-with-burpsuite**](/docs/user-guide/skills/optional/security/security-intercepting-mobile-traffic-with-burpsuite) | Intercepts and analyzes HTTP/HTTPS traffic from mobile |
| [**investigating-insider-threat-indicators**](/docs/user-guide/skills/optional/security/security-investigating-insider-threat-indicators) | Investigates insider threat indicators including data |
| [**investigating-phishing-email-incident**](/docs/user-guide/skills/optional/security/security-investigating-phishing-email-incident) | Investigates phishing email incidents from initial user |
| [**investigating-ransomware-attack-artifacts**](/docs/user-guide/skills/optional/security/security-investigating-ransomware-attack-artifacts) | Forensically preserve memory and disk, collect ransom notes |
| [**managing-cloud-identity-with-okta**](/docs/user-guide/skills/optional/security/security-managing-cloud-identity-with-okta) | Implement Okta as a centralized cloud identity provider |
| [**managing-intelligence-lifecycle**](/docs/user-guide/skills/optional/security/security-managing-intelligence-lifecycle) | Manages the end-to-end cyber threat intelligence lifecycle |
| [**managing-third-party-vendor-risk**](/docs/user-guide/skills/optional/security/security-managing-third-party-vendor-risk) | Build and run a third-party/vendor risk management (TPRM) |
| [**mapping-mitre-attack-techniques**](/docs/user-guide/skills/optional/security/security-mapping-mitre-attack-techniques) | Maps observed adversary behaviors, security alerts, and |
| [**migrating-to-post-quantum-cryptography**](/docs/user-guide/skills/optional/security/security-migrating-to-post-quantum-cryptography) | Build a cryptographic inventory/CBOM with OpenSSL 3.5+ |
| [**modeling-threats-with-opencti**](/docs/user-guide/skills/optional/security/security-modeling-threats-with-opencti) | Deploy OpenCTI (Filigran) via Docker Compose and use the |
| [**monitoring-darkweb-sources**](/docs/user-guide/skills/optional/security/security-monitoring-darkweb-sources) | Monitors dark web forums, marketplaces, paste sites, and |
| [**monitoring-scada-modbus-traffic-anomalies**](/docs/user-guide/skills/optional/security/security-monitoring-scada-modbus-traffic-anomalies) | Monitors Modbus TCP traffic on SCADA and ICS networks to |
| [**operationalizing-misp-threat-feeds**](/docs/user-guide/skills/optional/security/security-operationalizing-misp-threat-feeds) | Stand up MISP, enable and cache curated threat feeds |
| [**orchestrating-llm-attacks-with-pyrit**](/docs/user-guide/skills/optional/security/security-orchestrating-llm-attacks-with-pyrit) | Build automated multi-turn adversarial attacks against |
| [**oss-forensics**](/docs/user-guide/skills/optional/security/security-oss-forensics) | GitHub supply-chain forensics: recovery, IOCs, reporting. |
| [**parsing-artifacts-with-eric-zimmerman-tools**](/docs/user-guide/skills/optional/security/security-parsing-artifacts-with-eric-zimmerman-tools) | Parse Windows forensic artifacts—$MFT/$J (MFTECmd) |
| [**performing-access-recertification-with-saviynt**](/docs/user-guide/skills/optional/security/security-performing-access-recertification-with-saviynt) | Configure and execute access recertification campaigns in |
| [**performing-access-review-and-certification**](/docs/user-guide/skills/optional/security/security-performing-access-review-and-certification) | Designs and runs access review and certification |
| [**performing-active-directory-compromise-investigation**](/docs/user-guide/skills/optional/security/security-performing-active-directory-compromise-investigation) | Investigate Active Directory compromise by analyzing |
| [**performing-active-directory-vulnerability-assessment**](/docs/user-guide/skills/optional/security/security-performing-active-directory-vulnerability-assessment) | Assess Active Directory security posture using PingCastle |
| [**performing-adversary-in-the-middle-phishing-detection**](/docs/user-guide/skills/optional/security/security-performing-adversary-in-the-middle-phishing-detection) | Detect and respond to Adversary-in-the-Middle (AiTM) |
| [**performing-agentless-vulnerability-scanning**](/docs/user-guide/skills/optional/security/security-performing-agentless-vulnerability-scanning) | Configure and execute agentless vulnerability scanning |
| [**performing-ai-driven-osint-correlation**](/docs/user-guide/skills/optional/security/security-performing-ai-driven-osint-correlation) | Use AI/LLM-based reasoning with Sherlock, theHarvester, and |
| [**performing-alert-triage-with-elastic-siem**](/docs/user-guide/skills/optional/security/security-performing-alert-triage-with-elastic-siem) | Perform systematic alert triage in Elastic Security |
| [**performing-android-app-static-analysis-with-mobsf**](/docs/user-guide/skills/optional/security/security-performing-android-app-static-analysis-with-mobsf) | Performs automated static analysis of Android applications |
| [**performing-api-fuzzing-with-restler**](/docs/user-guide/skills/optional/security/security-performing-api-fuzzing-with-restler) | Uses Microsoft RESTler to perform stateful REST API |
| [**performing-api-inventory-and-discovery**](/docs/user-guide/skills/optional/security/security-performing-api-inventory-and-discovery) | Performs API inventory and discovery to identify all API |
| [**performing-api-rate-limiting-bypass**](/docs/user-guide/skills/optional/security/security-performing-api-rate-limiting-bypass) | Tests API rate limiting for bypass vulnerabilities using |
| [**performing-api-security-testing-with-postman**](/docs/user-guide/skills/optional/security/security-performing-api-security-testing-with-postman) | Uses Postman to build structured API security test |
| [**performing-arp-spoofing-attack-simulation**](/docs/user-guide/skills/optional/security/security-performing-arp-spoofing-attack-simulation) | Simulates ARP spoofing/cache-poisoning attacks in |
| [**performing-asset-criticality-scoring-for-vulns**](/docs/user-guide/skills/optional/security/security-performing-asset-criticality-scoring-for-vulns) | Build a multi-factor asset criticality scoring |
| [**performing-authenticated-scan-with-openvas**](/docs/user-guide/skills/optional/security/security-performing-authenticated-scan-with-openvas) | Configure and execute authenticated (credentialed) |
| [**performing-authenticated-vulnerability-scan**](/docs/user-guide/skills/optional/security/security-performing-authenticated-vulnerability-scan) | Plan and run authenticated (credentialed) vulnerability |
| [**performing-automated-malware-analysis-with-cape**](/docs/user-guide/skills/optional/security/security-performing-automated-malware-analysis-with-cape) | Deploy and operate the CAPEv2 malware sandbox (a Cuckoo |
| [**performing-aws-account-enumeration-with-scout-suite**](/docs/user-guide/skills/optional/security/security-performing-aws-account-enumeration-with-scout-suite) | Run the agentless, open-source ScoutSuite tool (via pip |
| [**performing-aws-privilege-escalation-assessment**](/docs/user-guide/skills/optional/security/security-performing-aws-privilege-escalation-assessment) | Performing authorized privilege escalation assessments in |
| [**performing-bandwidth-throttling-attack-simulation**](/docs/user-guide/skills/optional/security/security-performing-bandwidth-throttling-attack-simulation) | Simulate bandwidth throttling and network degradation |
| [**performing-blind-ssrf-exploitation**](/docs/user-guide/skills/optional/security/security-performing-blind-ssrf-exploitation) | Detect and exploit blind Server-Side Request Forgery (SSRF) |
| [**performing-bluetooth-security-assessment**](/docs/user-guide/skills/optional/security/security-performing-bluetooth-security-assessment) | Assess Bluetooth Low Energy (BLE) device security using |
| [**performing-brand-monitoring-for-impersonation**](/docs/user-guide/skills/optional/security/security-performing-brand-monitoring-for-impersonation) | Monitor for brand impersonation attacks across domains |
| [**performing-clickjacking-attack-test**](/docs/user-guide/skills/optional/security/security-performing-clickjacking-attack-test) | Testing web applications for clickjacking vulnerabilities |
| [**performing-cloud-asset-inventory-with-cartography**](/docs/user-guide/skills/optional/security/security-performing-cloud-asset-inventory-with-cartography) | Run Cartography to sync AWS, GCP, or Azure resources into a |
| [**performing-cloud-forensics-investigation**](/docs/user-guide/skills/optional/security/security-performing-cloud-forensics-investigation) | Collect and analyze cloud forensic evidence using AWS CLI |
| [**performing-cloud-forensics-with-aws-cloudtrail**](/docs/user-guide/skills/optional/security/security-performing-cloud-forensics-with-aws-cloudtrail) | Investigate AWS account compromise by querying CloudTrail |
| [**performing-cloud-incident-containment-procedures**](/docs/user-guide/skills/optional/security/security-performing-cloud-incident-containment-procedures) | Execute cloud-native incident containment across AWS |
| [**performing-cloud-log-forensics-with-athena**](/docs/user-guide/skills/optional/security/security-performing-cloud-log-forensics-with-athena) | Uses AWS Athena to query CloudTrail, VPC Flow Logs, S3 |
| [**performing-cloud-native-forensics-with-falco**](/docs/user-guide/skills/optional/security/security-performing-cloud-native-forensics-with-falco) | Uses Falco YAML rules for runtime threat detection in |
| [**performing-cloud-native-threat-hunting-with-aws-detective**](/docs/user-guide/skills/optional/security/security-performing-cloud-native-threat-hunting-with-aws-detective) | Investigate AWS security incidents using Amazon Detective's |
| [**performing-cloud-penetration-testing-with-pacu**](/docs/user-guide/skills/optional/security/security-performing-cloud-penetration-testing-with-pacu) | Run authorized AWS penetration tests with Pacu, the |
| [**performing-cloud-storage-forensic-acquisition**](/docs/user-guide/skills/optional/security/security-performing-cloud-storage-forensic-acquisition) | Perform forensic acquisition of cloud storage services |
| [**performing-container-escape-detection**](/docs/user-guide/skills/optional/security/security-performing-container-escape-detection) | Audits container and pod configuration for escape-enabling |
| [**performing-container-image-hardening**](/docs/user-guide/skills/optional/security/security-performing-container-image-hardening) | Harden container images by minimizing attack surface |
| [**performing-container-security-scanning-with-trivy**](/docs/user-guide/skills/optional/security/security-performing-container-security-scanning-with-trivy) | Runs Trivy across every target type it supports - container |
| [**performing-content-security-policy-bypass**](/docs/user-guide/skills/optional/security/security-performing-content-security-policy-bypass) | Analyze Content-Security-Policy headers and bypass them to |
| [**performing-cryptographic-audit-of-application**](/docs/user-guide/skills/optional/security/security-performing-cryptographic-audit-of-application) | A cryptographic audit systematically reviews an |
| [**performing-csrf-attack-simulation**](/docs/user-guide/skills/optional/security/security-performing-csrf-attack-simulation) | Testing web applications for Cross-Site Request Forgery |
| [**performing-cve-prioritization-with-kev-catalog**](/docs/user-guide/skills/optional/security/security-performing-cve-prioritization-with-kev-catalog) | Fetch and parse the CISA Known Exploited Vulnerabilities |
| [**performing-dark-web-monitoring-for-threats**](/docs/user-guide/skills/optional/security/security-performing-dark-web-monitoring-for-threats) | Dark web monitoring involves systematically scanning Tor |
| [**performing-deception-technology-deployment**](/docs/user-guide/skills/optional/security/security-performing-deception-technology-deployment) | Deploys deception technology including honeypots |
| [**performing-directory-traversal-testing**](/docs/user-guide/skills/optional/security/security-performing-directory-traversal-testing) | Test web applications for path traversal and Local/Remote |
| [**performing-disk-forensics-investigation**](/docs/user-guide/skills/optional/security/security-performing-disk-forensics-investigation) | Conduct disk forensics investigations using forensic |
| [**performing-dmarc-policy-enforcement-rollout**](/docs/user-guide/skills/optional/security/security-performing-dmarc-policy-enforcement-rollout) | Execute a phased DMARC rollout by inventorying sending |
| [**performing-dns-enumeration-and-zone-transfer**](/docs/user-guide/skills/optional/security/security-performing-dns-enumeration-and-zone-transfer) | Enumerates DNS records, attempts zone transfers |
| [**performing-dns-tunneling-detection**](/docs/user-guide/skills/optional/security/security-performing-dns-tunneling-detection) | Detects DNS tunneling by computing Shannon entropy of DNS |
| [**performing-docker-bench-security-assessment**](/docs/user-guide/skills/optional/security/security-performing-docker-bench-security-assessment) | Runs Docker Bench for Security, the open-source CIS Docker |
| [**performing-dynamic-analysis-of-android-app**](/docs/user-guide/skills/optional/security/security-performing-dynamic-analysis-of-android-app) | Performs runtime dynamic analysis of Android applications |
| [**performing-dynamic-analysis-with-any-run**](/docs/user-guide/skills/optional/security/security-performing-dynamic-analysis-with-any-run) | Perform interactive dynamic malware analysis using the |
| [**performing-endpoint-forensics-investigation**](/docs/user-guide/skills/optional/security/security-performing-endpoint-forensics-investigation) | Performs digital forensics investigation on compromised |
| [**performing-endpoint-vulnerability-remediation**](/docs/user-guide/skills/optional/security/security-performing-endpoint-vulnerability-remediation) | Performs vulnerability remediation on endpoints by |
| [**performing-entitlement-review-with-sailpoint-iiq**](/docs/user-guide/skills/optional/security/security-performing-entitlement-review-with-sailpoint-iiq) | Runs entitlement review and access certification campaigns |
| [**performing-false-positive-reduction-in-siem**](/docs/user-guide/skills/optional/security/security-performing-false-positive-reduction-in-siem) | Reduces SIEM false positives through systematic rule |
| [**performing-file-carving-with-foremost**](/docs/user-guide/skills/optional/security/security-performing-file-carving-with-foremost) | Recovers files from disk images and unallocated space using |
| [**performing-firmware-extraction-with-binwalk**](/docs/user-guide/skills/optional/security/security-performing-firmware-extraction-with-binwalk) | Performs firmware image extraction and analysis using |
| [**performing-firmware-malware-analysis**](/docs/user-guide/skills/optional/security/security-performing-firmware-malware-analysis) | Analyzes firmware images for embedded malware, backdoors |
| [**performing-fuzzing-with-aflplusplus**](/docs/user-guide/skills/optional/security/security-performing-fuzzing-with-aflplusplus) | Performs coverage-guided fuzzing of compiled binaries with |
| [**performing-gcp-penetration-testing-with-gcpbucketbrute**](/docs/user-guide/skills/optional/security/security-performing-gcp-penetration-testing-with-gcpbucketbrute) | Performs authorized GCP security testing using |
| [**performing-gcp-security-assessment-with-forseti**](/docs/user-guide/skills/optional/security/security-performing-gcp-security-assessment-with-forseti) | Performing comprehensive security assessments of Google |
| [**performing-graphql-depth-limit-attack**](/docs/user-guide/skills/optional/security/security-performing-graphql-depth-limit-attack) | Execute and test GraphQL depth limit attacks using deeply |
| [**performing-graphql-introspection-attack**](/docs/user-guide/skills/optional/security/security-performing-graphql-introspection-attack) | Performs GraphQL introspection attacks that extract the |
| [**performing-graphql-security-assessment**](/docs/user-guide/skills/optional/security/security-performing-graphql-security-assessment) | Assessing GraphQL API endpoints for introspection leaks |
| [**performing-hardware-security-module-integration**](/docs/user-guide/skills/optional/security/security-performing-hardware-security-module-integration) | Integrates Hardware Security Modules (HSMs) via the PKCS#11 |
| [**performing-hash-cracking-with-hashcat**](/docs/user-guide/skills/optional/security/security-performing-hash-cracking-with-hashcat) | Cracks password hashes with Hashcat, covering hash-type |
| [**performing-http-parameter-pollution-attack**](/docs/user-guide/skills/optional/security/security-performing-http-parameter-pollution-attack) | Executes HTTP Parameter Pollution attacks that inject |
| [**performing-ics-asset-discovery-with-claroty**](/docs/user-guide/skills/optional/security/security-performing-ics-asset-discovery-with-claroty) | Performs ICS/OT asset discovery with Claroty xDome |
| [**performing-indicator-lifecycle-management**](/docs/user-guide/skills/optional/security/security-performing-indicator-lifecycle-management) | Tracks IOCs through discovery, enrichment/validation |
| [**performing-insider-threat-investigation**](/docs/user-guide/skills/optional/security/security-performing-insider-threat-investigation) | Investigates insider threat incidents involving employees |
| [**performing-ioc-enrichment-automation**](/docs/user-guide/skills/optional/security/security-performing-ioc-enrichment-automation) | Automates Indicator of Compromise (IOC) enrichment by |
| [**performing-ios-app-security-assessment**](/docs/user-guide/skills/optional/security/security-performing-ios-app-security-assessment) | Performs comprehensive iOS application security assessments |
| [**performing-ip-reputation-analysis-with-shodan**](/docs/user-guide/skills/optional/security/security-performing-ip-reputation-analysis-with-shodan) | Analyze IP address reputation using the Shodan API to |
| [**performing-jwt-none-algorithm-attack**](/docs/user-guide/skills/optional/security/security-performing-jwt-none-algorithm-attack) | Execute and test the JWT none algorithm attack, crafting |
| [**performing-kubernetes-cis-benchmark-with-kube-bench**](/docs/user-guide/skills/optional/security/security-performing-kubernetes-cis-benchmark-with-kube-bench) | Turns kube-bench output into a finished CIS Kubernetes |
| [**performing-kubernetes-etcd-security-assessment**](/docs/user-guide/skills/optional/security/security-performing-kubernetes-etcd-security-assessment) | Assesses the security posture of the etcd cluster backing |
| [**performing-kubernetes-penetration-testing**](/docs/user-guide/skills/optional/security/security-performing-kubernetes-penetration-testing) | Evaluates Kubernetes cluster security by actively |
| [**performing-lateral-movement-detection**](/docs/user-guide/skills/optional/security/security-performing-lateral-movement-detection) | Detects lateral movement techniques including |
| [**performing-linux-log-forensics-investigation**](/docs/user-guide/skills/optional/security/security-performing-linux-log-forensics-investigation) | Perform forensic investigation of Linux system logs |
| [**performing-log-analysis-for-forensic-investigation**](/docs/user-guide/skills/optional/security/security-performing-log-analysis-for-forensic-investigation) | Collect, parse, and correlate system, application, and |
| [**performing-log-source-onboarding-in-siem**](/docs/user-guide/skills/optional/security/security-performing-log-source-onboarding-in-siem) | Perform structured log source onboarding into SIEM |
| [**performing-malware-hash-enrichment-with-virustotal**](/docs/user-guide/skills/optional/security/security-performing-malware-hash-enrichment-with-virustotal) | Enrich malware file hashes (MD5, SHA-1, SHA-256) using the |
| [**performing-malware-ioc-extraction**](/docs/user-guide/skills/optional/security/security-performing-malware-ioc-extraction) | Malware IOC extraction is the process of analyzing |
| [**performing-malware-persistence-investigation**](/docs/user-guide/skills/optional/security/security-performing-malware-persistence-investigation) | Systematically investigate all persistence mechanisms on |
| [**performing-malware-triage-with-yara**](/docs/user-guide/skills/optional/security/security-performing-malware-triage-with-yara) | Performs rapid malware triage and classification using YARA |
| [**performing-memory-forensics-with-volatility3**](/docs/user-guide/skills/optional/security/security-performing-memory-forensics-with-volatility3) | Analyze volatile memory (RAM) dumps using the Volatility 3 |
| [**performing-memory-forensics-with-volatility3-plugins**](/docs/user-guide/skills/optional/security/security-performing-memory-forensics-with-volatility3-plugins) | Analyze memory dumps using Volatility3 plugins to detect |
| [**performing-mobile-app-certificate-pinning-bypass**](/docs/user-guide/skills/optional/security/security-performing-mobile-app-certificate-pinning-bypass) | Bypasses SSL/TLS certificate pinning implementations in |
| [**performing-mobile-device-forensics-with-cellebrite**](/docs/user-guide/skills/optional/security/security-performing-mobile-device-forensics-with-cellebrite) | Acquire and analyze mobile device data using Cellebrite |
| [**performing-network-forensics-with-wireshark**](/docs/user-guide/skills/optional/security/security-performing-network-forensics-with-wireshark) | Capture and analyze network traffic using Wireshark and |
| [**performing-network-packet-capture-analysis**](/docs/user-guide/skills/optional/security/security-performing-network-packet-capture-analysis) | Perform forensic analysis of network packet captures |
| [**performing-network-traffic-analysis-with-tshark**](/docs/user-guide/skills/optional/security/security-performing-network-traffic-analysis-with-tshark) | Automate network traffic analysis using tshark (Wireshark |
| [**performing-network-traffic-analysis-with-zeek**](/docs/user-guide/skills/optional/security/security-performing-network-traffic-analysis-with-zeek) | Deploy Zeek (formerly Bro) as a passive network security |
| [**performing-nist-csf-maturity-assessment**](/docs/user-guide/skills/optional/security/security-performing-nist-csf-maturity-assessment) | Conduct a NIST Cybersecurity Framework (CSF) 2.0 maturity |
| [**performing-oauth-scope-minimization-review**](/docs/user-guide/skills/optional/security/security-performing-oauth-scope-minimization-review) | Performs OAuth 2.0 scope minimization review to identify |
| [**performing-oil-gas-cybersecurity-assessment**](/docs/user-guide/skills/optional/security/security-performing-oil-gas-cybersecurity-assessment) | Conduct cybersecurity assessments of upstream, midstream |
| [**performing-osint-with-spiderfoot**](/docs/user-guide/skills/optional/security/security-performing-osint-with-spiderfoot) | Automate OSINT collection with the SpiderFoot REST API and |
| [**performing-ot-network-security-assessment**](/docs/user-guide/skills/optional/security/security-performing-ot-network-security-assessment) | This skill covers conducting comprehensive security |
| [**performing-ot-vulnerability-assessment-with-claroty**](/docs/user-guide/skills/optional/security/security-performing-ot-vulnerability-assessment-with-claroty) | Perform OT vulnerability assessments using the Claroty |
| [**performing-ot-vulnerability-scanning-safely**](/docs/user-guide/skills/optional/security/security-performing-ot-vulnerability-scanning-safely) | Perform vulnerability scanning in OT/ICS environments |
| [**performing-packet-injection-attack**](/docs/user-guide/skills/optional/security/security-performing-packet-injection-attack) | Crafts and injects custom network packets using Scapy |
| [**performing-paste-site-monitoring-for-credentials**](/docs/user-guide/skills/optional/security/security-performing-paste-site-monitoring-for-credentials) | Monitor paste sites like Pastebin and GitHub Gists for |
| [**performing-phishing-simulation-with-gophish**](/docs/user-guide/skills/optional/security/security-performing-phishing-simulation-with-gophish) | Deploy and run authorized phishing awareness campaigns with |
| [**performing-plc-firmware-security-analysis**](/docs/user-guide/skills/optional/security/security-performing-plc-firmware-security-analysis) | This skill covers analyzing Programmable Logic Controller |
| [**performing-post-quantum-cryptography-migration**](/docs/user-guide/skills/optional/security/security-performing-post-quantum-cryptography-migration) | Assesses organizational readiness for post-quantum |
| [**performing-power-grid-cybersecurity-assessment**](/docs/user-guide/skills/optional/security/security-performing-power-grid-cybersecurity-assessment) | Conduct cybersecurity assessments of power grid |
| [**performing-privacy-impact-assessment**](/docs/user-guide/skills/optional/security/security-performing-privacy-impact-assessment) | Automates the Privacy Impact Assessment (PIA) workflow |
| [**performing-privileged-account-access-review**](/docs/user-guide/skills/optional/security/security-performing-privileged-account-access-review) | Conducts systematic reviews of privileged accounts to |
| [**performing-privileged-account-discovery**](/docs/user-guide/skills/optional/security/security-performing-privileged-account-discovery) | Discovers and inventories privileged accounts across |
| [**performing-purple-team-exercise**](/docs/user-guide/skills/optional/security/security-performing-purple-team-exercise) | Performs purple team exercises by coordinating red team |
| [**performing-ransomware-response**](/docs/user-guide/skills/optional/security/security-performing-ransomware-response) | Executes a structured ransomware incident response from |
| [**performing-ransomware-tabletop-exercise**](/docs/user-guide/skills/optional/security/security-performing-ransomware-tabletop-exercise) | Plans and facilitates tabletop exercises simulating |
| [**performing-red-team-phishing-with-gophish**](/docs/user-guide/skills/optional/security/security-performing-red-team-phishing-with-gophish) | Automates GoPhish phishing simulation campaigns using the |
| [**performing-s7comm-protocol-security-analysis**](/docs/user-guide/skills/optional/security/security-performing-s7comm-protocol-security-analysis) | Perform security analysis of Siemens S7comm and S7CommPlus |
| [**performing-sca-dependency-scanning-with-snyk**](/docs/user-guide/skills/optional/security/security-performing-sca-dependency-scanning-with-snyk) | This skill covers implementing Software Composition |
| [**performing-scada-hmi-security-assessment**](/docs/user-guide/skills/optional/security/security-performing-scada-hmi-security-assessment) | Perform security assessments of SCADA Human-Machine |
| [**performing-second-order-sql-injection**](/docs/user-guide/skills/optional/security/security-performing-second-order-sql-injection) | Detect and exploit second-order SQL injection |
| [**performing-security-headers-audit**](/docs/user-guide/skills/optional/security/security-performing-security-headers-audit) | Auditing HTTP security headers including CSP, HSTS |
| [**performing-serverless-function-security-review**](/docs/user-guide/skills/optional/security/security-performing-serverless-function-security-review) | Performing security reviews of serverless functions across |
| [**performing-service-account-audit**](/docs/user-guide/skills/optional/security/security-performing-service-account-audit) | Audit service accounts across enterprise infrastructure to |
| [**performing-service-account-credential-rotation**](/docs/user-guide/skills/optional/security/security-performing-service-account-credential-rotation) | Automates credential rotation for service accounts across |
| [**performing-soap-web-service-security-testing**](/docs/user-guide/skills/optional/security/security-performing-soap-web-service-security-testing) | Performs security testing of SOAP web services by analyzing |
| [**performing-soc-tabletop-exercise**](/docs/user-guide/skills/optional/security/security-performing-soc-tabletop-exercise) | Performs tabletop exercises for SOC teams simulating |
| [**performing-soc2-type2-audit-preparation**](/docs/user-guide/skills/optional/security/security-performing-soc2-type2-audit-preparation) | Automates SOC 2 Type II audit preparation including gap |
| [**performing-sqlite-database-forensics**](/docs/user-guide/skills/optional/security/security-performing-sqlite-database-forensics) | Performs forensic analysis of SQLite databases by examining |
| [**performing-ssl-certificate-lifecycle-management**](/docs/user-guide/skills/optional/security/security-performing-ssl-certificate-lifecycle-management) | Automates the full SSL/TLS certificate lifecycle, including |
| [**performing-ssl-stripping-attack**](/docs/user-guide/skills/optional/security/security-performing-ssl-stripping-attack) | Simulates SSL stripping / HTTPS downgrade attacks using |
| [**performing-ssl-tls-inspection-configuration**](/docs/user-guide/skills/optional/security/security-performing-ssl-tls-inspection-configuration) | Configure SSL/TLS break-and-inspect on next-generation |
| [**performing-ssl-tls-security-assessment**](/docs/user-guide/skills/optional/security/security-performing-ssl-tls-security-assessment) | Assess SSL/TLS server configurations using the sslyze |
| [**performing-ssrf-vulnerability-exploitation**](/docs/user-guide/skills/optional/security/security-performing-ssrf-vulnerability-exploitation) | Tests web application URL parameters for Server-Side |
| [**performing-static-malware-analysis-with-pe-studio**](/docs/user-guide/skills/optional/security/security-performing-static-malware-analysis-with-pe-studio) | Performs static analysis of Windows PE malware samples |
| [**performing-steganography-detection**](/docs/user-guide/skills/optional/security/security-performing-steganography-detection) | Detects and extracts hidden data embedded in images, audio |
| [**performing-subdomain-enumeration-with-subfinder**](/docs/user-guide/skills/optional/security/security-performing-subdomain-enumeration-with-subfinder) | Enumerate subdomains of target domains using |
| [**performing-supply-chain-attack-simulation**](/docs/user-guide/skills/optional/security/security-performing-supply-chain-attack-simulation) | Simulates and detects software supply chain attacks |
| [**performing-threat-emulation-with-atomic-red-team**](/docs/user-guide/skills/optional/security/security-performing-threat-emulation-with-atomic-red-team) | Executes Atomic Red Team tests for MITRE ATT&CK technique |
| [**performing-threat-hunting-with-elastic-siem**](/docs/user-guide/skills/optional/security/security-performing-threat-hunting-with-elastic-siem) | Performs proactive threat hunting in Elastic Security SIEM |
| [**performing-threat-hunting-with-yara-rules**](/docs/user-guide/skills/optional/security/security-performing-threat-hunting-with-yara-rules) | Use YARA pattern-matching rules to hunt for malware |
| [**performing-threat-intelligence-sharing-with-misp**](/docs/user-guide/skills/optional/security/security-performing-threat-intelligence-sharing-with-misp) | Uses PyMISP (the official MISP REST API library) to create |
| [**performing-threat-landscape-assessment-for-sector**](/docs/user-guide/skills/optional/security/security-performing-threat-landscape-assessment-for-sector) | Conducts a sector-specific threat landscape assessment |
| [**performing-threat-modeling-with-owasp-threat-dragon**](/docs/user-guide/skills/optional/security/security-performing-threat-modeling-with-owasp-threat-dragon) | Uses OWASP Threat Dragon (web or desktop) to build data |
| [**performing-timeline-reconstruction-with-plaso**](/docs/user-guide/skills/optional/security/security-performing-timeline-reconstruction-with-plaso) | Builds comprehensive forensic super-timelines using Plaso |
| [**performing-user-behavior-analytics**](/docs/user-guide/skills/optional/security/security-performing-user-behavior-analytics) | Performs User and Entity Behavior Analytics (UEBA) to |
| [**performing-vlan-hopping-attack**](/docs/user-guide/skills/optional/security/security-performing-vlan-hopping-attack) | Simulates VLAN hopping attacks using switch spoofing and |
| [**performing-web-application-firewall-bypass**](/docs/user-guide/skills/optional/security/security-performing-web-application-firewall-bypass) | Bypasses Web Application Firewall protections using |
| [**performing-web-application-scanning-with-nikto**](/docs/user-guide/skills/optional/security/security-performing-web-application-scanning-with-nikto) | Runs Nikto, an open-source web server and web application |
| [**performing-web-application-vulnerability-triage**](/docs/user-guide/skills/optional/security/security-performing-web-application-vulnerability-triage) | Triages web application vulnerability findings from |
| [**performing-web-cache-deception-attack**](/docs/user-guide/skills/optional/security/security-performing-web-cache-deception-attack) | Executes web cache deception attacks by exploiting path |
| [**performing-web-cache-poisoning-attack**](/docs/user-guide/skills/optional/security/security-performing-web-cache-poisoning-attack) | Exploiting web cache mechanisms to serve malicious content |
| [**performing-wifi-password-cracking-with-aircrack**](/docs/user-guide/skills/optional/security/security-performing-wifi-password-cracking-with-aircrack) | Captures WPA/WPA2 handshakes and performs offline password |
| [**performing-windows-artifact-analysis-with-eric-zimmerman-tools**](/docs/user-guide/skills/optional/security/security-performing-windows-artifact-analysis-with-eric-zimmerman-tools) | Performs comprehensive Windows forensic artifact analysis |
| [**performing-wireless-security-assessment-with-kismet**](/docs/user-guide/skills/optional/security/security-performing-wireless-security-assessment-with-kismet) | Conduct wireless network security assessments using Kismet |
| [**performing-yara-rule-development-for-detection**](/docs/user-guide/skills/optional/security/security-performing-yara-rule-development-for-detection) | Develops precise YARA and YARA-X rules for malware |
| [**post-exploiting-microsoft-graph-with-graphrunner**](/docs/user-guide/skills/optional/security/security-post-exploiting-microsoft-graph-with-graphrunner) | Runs GraphRunner, a PowerShell post-exploitation toolset |
| [**prioritizing-vulnerabilities-with-cvss-scoring**](/docs/user-guide/skills/optional/security/security-prioritizing-vulnerabilities-with-cvss-scoring) | The Common Vulnerability Scoring System (CVSS) is the |
| [**processing-stix-taxii-feeds**](/docs/user-guide/skills/optional/security/security-processing-stix-taxii-feeds) | Processes STIX 2.1 threat intelligence bundles delivered |
| [**profiling-threat-actor-groups**](/docs/user-guide/skills/optional/security/security-profiling-threat-actor-groups) | Develops comprehensive threat actor profiles for APT |
| [**recovering-deleted-files-with-photorec**](/docs/user-guide/skills/optional/security/security-recovering-deleted-files-with-photorec) | Recovers deleted files from disk images and storage media |
| [**recovering-from-ransomware-attack**](/docs/user-guide/skills/optional/security/security-recovering-from-ransomware-attack) | Executes structured ransomware incident recovery following |
| [**red-teaming-llms-with-garak**](/docs/user-guide/skills/optional/security/security-red-teaming-llms-with-garak) | Runs NVIDIA garak probe suites (jailbreak, prompt |
| [**remediating-s3-bucket-misconfiguration**](/docs/user-guide/skills/optional/security/security-remediating-s3-bucket-misconfiguration) | Provides step-by-step procedures for remediating Amazon S3 |
| [**reverse-engineering-android-malware-with-jadx**](/docs/user-guide/skills/optional/security/security-reverse-engineering-android-malware-with-jadx) | Reverse engineers malicious Android APK files using the |
| [**reverse-engineering-dotnet-malware-with-dnspy**](/docs/user-guide/skills/optional/security/security-reverse-engineering-dotnet-malware-with-dnspy) | Reverse engineers .NET malware samples using the dnSpy |
| [**reverse-engineering-ios-app-with-frida**](/docs/user-guide/skills/optional/security/security-reverse-engineering-ios-app-with-frida) | Reverse engineers iOS applications using Frida dynamic |
| [**reverse-engineering-malware-with-ghidra**](/docs/user-guide/skills/optional/security/security-reverse-engineering-malware-with-ghidra) | Reverse engineers malware binaries using NSA's Ghidra |
| [**reverse-engineering-ransomware-encryption-routine**](/docs/user-guide/skills/optional/security/security-reverse-engineering-ransomware-encryption-routine) | Reverse engineer ransomware encryption routines to identify |
| [**reverse-engineering-rust-malware**](/docs/user-guide/skills/optional/security/security-reverse-engineering-rust-malware) | Reverse engineers Rust-compiled malware using IDA Pro and |
| [**scanning-container-images-with-grype**](/docs/user-guide/skills/optional/security/security-scanning-container-images-with-grype) | Scans container images, filesystems, and SBOMs for known |
| [**scanning-containers-with-trivy-in-cicd**](/docs/user-guide/skills/optional/security/security-scanning-containers-with-trivy-in-cicd) | Integrates Aqua Security's Trivy scanner into CI/CD |
| [**scanning-docker-images-with-trivy**](/docs/user-guide/skills/optional/security/security-scanning-docker-images-with-trivy) | Scans a Docker image with Trivy for vulnerabilities in OS |
| [**scanning-iac-and-images-with-trivy**](/docs/user-guide/skills/optional/security/security-scanning-iac-and-images-with-trivy) | Scans container images, Infrastructure-as-Code (Terraform |
| [**scanning-infrastructure-with-nessus**](/docs/user-guide/skills/optional/security/security-scanning-infrastructure-with-nessus) | Tenable Nessus is the industry-leading vulnerability |
| [**scanning-kubernetes-manifests-with-kubesec**](/docs/user-guide/skills/optional/security/security-scanning-kubernetes-manifests-with-kubesec) | Scores Kubernetes resource manifests with Kubesec to flag |
| [**scanning-network-with-nmap-advanced**](/docs/user-guide/skills/optional/security/security-scanning-network-with-nmap-advanced) | Performs advanced network recon using Nmap's Scripting |
| [**securing-agentic-ai-tool-invocation**](/docs/user-guide/skills/optional/security/security-securing-agentic-ai-tool-invocation) | Implements defense-in-depth controls at an AI agent's |
| [**securing-api-gateway-with-aws-waf**](/docs/user-guide/skills/optional/security/security-securing-api-gateway-with-aws-waf) | Secures AWS API Gateway endpoints with AWS WAF by |
| [**securing-aws-iam-permissions**](/docs/user-guide/skills/optional/security/security-securing-aws-iam-permissions) | Hardens AWS IAM configurations to enforce least-privilege |
| [**securing-aws-lambda-execution-roles**](/docs/user-guide/skills/optional/security/security-securing-aws-lambda-execution-roles) | Hardens AWS Lambda execution roles by writing |
| [**securing-azure-with-microsoft-defender**](/docs/user-guide/skills/optional/security/security-securing-azure-with-microsoft-defender) | Deploys and configures Microsoft Defender for Cloud as a |
| [**securing-container-registry-images**](/docs/user-guide/skills/optional/security/security-securing-container-registry-images) | Secures container registry images (ECR, ACR, GCR, Docker |
| [**securing-container-registry-with-harbor**](/docs/user-guide/skills/optional/security/security-securing-container-registry-with-harbor) | Configures the security features of the Harbor open-source |
| [**securing-github-actions-workflows**](/docs/user-guide/skills/optional/security/security-securing-github-actions-workflows) | Hardens GitHub Actions workflows against supply chain |
| [**securing-helm-chart-deployments**](/docs/user-guide/skills/optional/security/security-securing-helm-chart-deployments) | Secures Helm chart deployments by verifying chart |
| [**securing-historian-server-in-ot-environment**](/docs/user-guide/skills/optional/security/security-securing-historian-server-in-ot-environment) | Audits and hardens process historian servers (OSIsoft PI |
| [**securing-kubernetes-on-cloud**](/docs/user-guide/skills/optional/security/security-securing-kubernetes-on-cloud) | Hardens managed Kubernetes clusters on EKS, AKS, and GKE by |
| [**securing-remote-access-to-ot-environment**](/docs/user-guide/skills/optional/security/security-securing-remote-access-to-ot-environment) | Designs and configures secure remote access to OT/ICS |
| [**securing-serverless-functions**](/docs/user-guide/skills/optional/security/security-securing-serverless-functions) | Hardens serverless compute platforms (AWS Lambda, Azure |
| [**sherlock**](/docs/user-guide/skills/optional/security/security-sherlock) | Find accounts for a username across 400+ platforms. |
| [**testing-android-intents-for-vulnerabilities**](/docs/user-guide/skills/optional/security/security-testing-android-intents-for-vulnerabilities) | Tests Android inter-process communication (IPC) through |
| [**testing-api-authentication-weaknesses**](/docs/user-guide/skills/optional/security/security-testing-api-authentication-weaknesses) | Tests API authentication mechanisms for weaknesses |
| [**testing-api-for-broken-object-level-authorization**](/docs/user-guide/skills/optional/security/security-testing-api-for-broken-object-level-authorization) | Tests REST and GraphQL APIs for Broken Object Level |
| [**testing-api-for-mass-assignment-vulnerability**](/docs/user-guide/skills/optional/security/security-testing-api-for-mass-assignment-vulnerability) | Tests APIs for mass assignment (auto-binding), OWASP |
| [**testing-api-security-with-owasp-top-10**](/docs/user-guide/skills/optional/security/security-testing-api-security-with-owasp-top-10) | Systematically assesses REST, GraphQL, and gRPC API |
| [**testing-cors-misconfiguration**](/docs/user-guide/skills/optional/security/security-testing-cors-misconfiguration) | Identifying and exploiting Cross-Origin Resource Sharing |
| [**testing-for-broken-access-control**](/docs/user-guide/skills/optional/security/security-testing-for-broken-access-control) | Systematically tests web applications and APIs for broken |
| [**testing-for-business-logic-vulnerabilities**](/docs/user-guide/skills/optional/security/security-testing-for-business-logic-vulnerabilities) | Manually identifies flaws in application business logic - |
| [**testing-for-email-header-injection**](/docs/user-guide/skills/optional/security/security-testing-for-email-header-injection) | Tests web application email functionality (contact forms |
| [**testing-for-host-header-injection**](/docs/user-guide/skills/optional/security/security-testing-for-host-header-injection) | Test web applications for HTTP Host header injection |
| [**testing-for-json-web-token-vulnerabilities**](/docs/user-guide/skills/optional/security/security-testing-for-json-web-token-vulnerabilities) | Tests JWT implementations for algorithm confusion, "none" |
| [**testing-for-open-redirect-vulnerabilities**](/docs/user-guide/skills/optional/security/security-testing-for-open-redirect-vulnerabilities) | Identifies and exploits open redirect vulnerabilities by |
| [**testing-for-sensitive-data-exposure**](/docs/user-guide/skills/optional/security/security-testing-for-sensitive-data-exposure) | Identifying sensitive data exposure vulnerabilities |
| [**testing-for-system-prompt-leakage**](/docs/user-guide/skills/optional/security/security-testing-for-system-prompt-leakage) | Extracts LLM system prompts using direct requests |
| [**testing-for-xml-injection-vulnerabilities**](/docs/user-guide/skills/optional/security/security-testing-for-xml-injection-vulnerabilities) | Test web applications for XML injection vulnerabilities |
| [**testing-for-xss-vulnerabilities-with-burpsuite**](/docs/user-guide/skills/optional/security/security-testing-for-xss-vulnerabilities-with-burpsuite) | Identifying and validating cross-site scripting |
| [**testing-for-xxe-injection-vulnerabilities**](/docs/user-guide/skills/optional/security/security-testing-for-xxe-injection-vulnerabilities) | Discovering and exploiting XML External Entity injection |
| [**testing-jwt-token-security**](/docs/user-guide/skills/optional/security/security-testing-jwt-token-security) | Assessing JSON Web Token implementations for cryptographic |
| [**testing-mobile-api-authentication**](/docs/user-guide/skills/optional/security/security-testing-mobile-api-authentication) | Tests authentication and authorization mechanisms in mobile |
| [**testing-oauth2-implementation-flaws**](/docs/user-guide/skills/optional/security/security-testing-oauth2-implementation-flaws) | Tests OAuth 2.0 and OpenID Connect implementations for |
| [**testing-prompt-injection-in-rag-pipelines**](/docs/user-guide/skills/optional/security/security-testing-prompt-injection-in-rag-pipelines) | Probes Retrieval-Augmented Generation pipelines for |
| [**testing-ransomware-recovery-procedures**](/docs/user-guide/skills/optional/security/security-testing-ransomware-recovery-procedures) | Tests and validates ransomware recovery procedures - backup |
| [**testing-websocket-api-security**](/docs/user-guide/skills/optional/security/security-testing-websocket-api-security) | Tests WebSocket API implementations for missing |
| [**tracking-threat-actor-infrastructure**](/docs/user-guide/skills/optional/security/security-tracking-threat-actor-infrastructure) | Discovers and maps adversary-controlled infrastructure (C2 |
| [**triaging-security-alerts-in-splunk**](/docs/user-guide/skills/optional/security/security-triaging-security-alerts-in-splunk) | Triages security alerts in Splunk Enterprise Security by |
| [**triaging-security-incident**](/docs/user-guide/skills/optional/security/security-triaging-security-incident) | Performs initial triage of security incidents using the |
| [**triaging-security-incident-with-ir-playbook**](/docs/user-guide/skills/optional/security/security-triaging-security-incident-with-ir-playbook) | Classifies and prioritizes security incidents using |
| [**triaging-vulnerabilities-with-ssvc-framework**](/docs/user-guide/skills/optional/security/security-triaging-vulnerabilities-with-ssvc-framework) | Triages and prioritizes vulnerabilities with CISA's |
| [**triaging-windows-with-kape**](/docs/user-guide/skills/optional/security/security-triaging-windows-with-kape) | Runs KAPE (Kroll Artifact Parser and Extractor) to collect |
| [**unbroker**](/docs/user-guide/skills/optional/security/security-unbroker) | Autonomously remove your info from data-broker sites. |
| [**validating-backup-integrity-for-recovery**](/docs/user-guide/skills/optional/security/security-validating-backup-integrity-for-recovery) | Validates backup integrity through cryptographic hash |
| [**validating-tpm-measured-boot-attestation**](/docs/user-guide/skills/optional/security/security-validating-tpm-measured-boot-attestation) | Verifies TPM 2.0 measured-boot integrity and remote |
| [**verifying-build-provenance-with-slsa-sigstore**](/docs/user-guide/skills/optional/security/security-verifying-build-provenance-with-slsa-sigstore) | Verifies artifact signatures and SLSA provenance using |
| [**web-pentest**](/docs/user-guide/skills/optional/security/security-web-pentest) | Authorized web pentest: recon, proof-based exploits, report. |

## smart-home

| Skill | Description |
|-------|-------------|
| [**openhue**](/docs/user-guide/skills/optional/smart-home/smart-home-openhue) | Control Philips Hue lights, scenes, rooms via OpenHue CLI. |

## software-development

| Skill | Description |
|-------|-------------|
| [**ast-grep**](/docs/user-guide/skills/optional/software-development/software-development-ast-grep) | AST-aware structural code search and rewrite via ast-grep. |
| [**code-wiki**](/docs/user-guide/skills/optional/software-development/software-development-code-wiki) | Generate wiki docs + Mermaid diagrams for any codebase. |
| [**grill-me**](/docs/user-guide/skills/optional/software-development/software-development-grill-me) | Adversarial plan interview before implementation. |
| [**rest-graphql-debug**](/docs/user-guide/skills/optional/software-development/software-development-rest-graphql-debug) | Debug REST/GraphQL APIs: status codes, auth, schemas, repro. |
| [**subagent-driven-development**](/docs/user-guide/skills/optional/software-development/software-development-subagent-driven-development) | Execute plans via delegate_task subagents (2-stage review). |

## web-development

| Skill | Description |
|-------|-------------|
| [**cloudflare-temporary-deploy**](/docs/user-guide/skills/optional/web-development/web-development-cloudflare-temporary-deploy) | Deploy a Worker live, no account, via wrangler --temporary. |
| [**har-derived-api-client**](/docs/user-guide/skills/optional/web-development/web-development-har-derived-api-client) | Record a site's XHR into a HAR, derive an HTTP client. |
| [**page-agent**](/docs/user-guide/skills/optional/web-development/web-development-page-agent) | Embed an in-page natural-language GUI copilot in web apps. |
| [**publish-site**](/docs/user-guide/skills/optional/web-development/web-development-publish-site) | Versioned site deploys to GitHub/Cloudflare/Netlify Pages. |

## yuanbao

| Skill | Description |
|-------|-------------|
| [**yuanbao**](/docs/user-guide/skills/optional/yuanbao/yuanbao-yuanbao) | Yuanbao (元宝) groups: @mention users, query info/members. |

---

## Contributing Optional Skills

To add a new optional skill to the repository:

1. Create a directory under `optional-skills/<category>/<skill-name>/`
2. Add a `SKILL.md` with standard frontmatter (name, description, version, author)
3. Include any supporting files in `references/`, `templates/`, or `scripts/` subdirectories
4. Submit a pull request — the skill will appear in this catalog and get its own docs page once merged
