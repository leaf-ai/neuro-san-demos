# WWAW

The **wwaw**, which stands for worldwide agentic web, is an app that can generate arbitrarily sized agent networks
using the web as a template for the agent connections and content.

This is a good tool to build large agent networks to measure how much you can scale and how wide and deep you can get
with agent networks on NeuroSAN.

**Note**: If the generated agentic systems are too large then running them may end up being costly.

---

## File

[build_wwaw.py](../../apps/wwaw/build_wwaw.py)

---

## Prerequisites

- Set the constants at the top of the file to point it at a start page on the web, and give it the target number of
agents.
- The app will generate an agent network hocon and store it in the registries directory.
- Add the name of the generated agent network to the manifest in order to run it.

---

## Description

The app starts at the start URL, generates an agent for each page and gives it instructions so the agent can represent
the text content of the page. It then adds any links from the page to be down-chain agents to this agent, and continues
on until it hits the max agents threshold.

Agents are typically somewhat limited on how many tools they can handle, so the script has a max-down-chains setting
and automatically creates intermediary agents to manage agent fanout.

Pages that are smaller than 200 characters are skipped.

The agent names are shortened.
