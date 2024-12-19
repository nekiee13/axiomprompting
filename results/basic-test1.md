## Basic Test 1

**Axiom Prompt**

**Objective:** Generate a factual summary detailing the history of the Eiffel Tower.

**Formalism:**

Maximize: Σ ∆ID(token, i | "history of the Eiffel Tower", L=100)

Subject to:

*   ∀token ∈ Tokens, context(token, C) ∧ structure(token, S) ∧ coherence(token, R) ∧ factuality(token, F)

**Constraints and Definitions:**

*   **L = 100:** The target length of the summary is 100 words.
*   **∆ID(token, i | "history of the Eiffel Tower", L):** The information gain of each token at position 'i' should specifically contribute to a factual account of the Eiffel Tower's history, given the length constraint. Prioritize tokens that convey key historical facts, dates, and events related to the Eiffel Tower.
*   **context(token, C):** Each token must be contextually relevant to the history of the Eiffel Tower and the preceding text in the summary.
*   **structure(token, S):** Each token must adhere to standard English grammar, syntax, and punctuation rules, forming grammatically correct sentences.
*   **coherence(token, R):** The sequence of tokens must form a logically structured and coherent narrative that is easy to understand and flows smoothly.
*   **factuality(token, F):** Each token must represent verifiable historical information about the Eiffel Tower. Avoid any speculation or unverified claims. This is a new addition that further grounds the model in reality.

**Output Instructions:**

Produce a concise and informative summary of the Eiffel Tower's history, strictly adhering to the defined formalism and constraints. Ensure the summary is approximately 100 words long, factually accurate, and well-written.


**Standard NLP Prompt:**

**Task:** Write a 100-word summary of the history of the Eiffel Tower.

**Instructions:**

*   Focus on providing a factual account of the Eiffel Tower's history.
*   Include key dates, events, and people involved in its construction and history.
*   Ensure the summary is accurate and does not contain any false information.
*   Write in clear, concise, and grammatically correct English.
*   Keep the summary to approximately 100 words.

*   **Output Instructions:**

Produce a concise and informative summary of the Eiffel Tower's history, strictly adhering to the defined formalism and constraints. Ensure the summary is approximately 100 words long, factually accurate, and well-written.
