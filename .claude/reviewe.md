# CHI Reviewer Checklist for AROMA

Apply these rules when reviewing any AROMA document. Be adversarial. A weak paper that passes internal review wastes a submission cycle.

---

## 1. Contribution

- [ ] **Is the contribution stated in one sentence?** If it takes a paragraph to explain what the paper contributes, it's not clear enough.
- [ ] **Is it an HCI contribution, not a psychology or NLP contribution?** CHI reviewers ask: "What does this change about how we design, build, or evaluate interactive systems?" If the answer is only theoretical, it's a journal paper, not CHI.
- [ ] **Does it advance or reorganize?** A taxonomy that reorganizes existing knowledge without producing new analytical leverage (predictions, design implications, evaluation criteria) will be rejected as "a literature review with a table."
- [ ] **Is "first" justified?** Every "first" claim must be defended with evidence of absence. If you say "first taxonomy of X," you must show you searched for prior taxonomies of X and found none. Cite the gap, don't just assert it.
- [ ] **Are there exactly 3 contributions?** CHI papers with 1 contribution feel thin. Papers with 5+ feel unfocused. Aim for 3 distinct, non-overlapping contributions.

---

## 2. Theoretical Grounding

- [ ] **Is each theory doing structural work?** Every cited theory must load-bear — it must define a dimension, justify a method, or constrain a design decision. If removing a citation changes nothing about the framework, the citation is decorative. Cut it.
- [ ] **Are citations accurate?** Does the cited paper actually say what you claim it says? Misrepresenting a source (even by overextension) is the fastest way to lose reviewer trust. Flag any citation you haven't read in full with `[^verify]`.
- [ ] **Is the theory falsifiable?** Can the framework be wrong? If no observation could contradict the taxonomy, it's not a scientific framework — it's a vocabulary list. State what would disprove or require revision of the framework.
- [ ] **Are terms defined before use?** Every technical term (role-taking, role-locking, obligation gap, structural binding) must be defined on first use. If a reader needs to read a different section to understand the current one, the structure is wrong.
- [ ] **Is the causal logic explicit?** If A causes B causes C, say so. Don't present A, B, and C as parallel observations and leave the reader to infer the chain. Specifically: distinguish between structural conditions, their consequences, and their experiential effects.
- [ ] **Are analogies earning their keep?** An analogy (e.g., "analogous to therapeutic misconception") is not an argument. It's an illustration. If the analogy is doing the work of the argument, the argument is missing.

---

## 3. Methodology (Taxonomy Papers)

- [ ] **Is the construction method cited and followed?** Nickerson et al. (2013) requires: ending conditions, iterative development, conceptual-to-empirical and empirical-to-conceptual cycles. If you cite the method, you must show compliance with its requirements.
- [ ] **Are ending conditions defined?** When is the taxonomy done? Nickerson's conditions: (a) all objects classifiable, (b) no new dimensions from new objects, (c) each dimension discriminates. State these explicitly and report whether they're met.
- [ ] **Is there empirical grounding, not just theoretical derivation?** A top-down-only taxonomy is a hypothesis. It needs bottom-up validation (corpus analysis, user study, expert review) to be a contribution. State which phases provide this and whether they're complete.
- [ ] **Are inclusion/exclusion criteria for taxonomy elements explicit?** Why 6 roles and not 5 or 8? Every included element needs a criterion. Every excluded element needs a documented reason. "Connector excluded: 1 paper, below threshold" is good. Silently omitting alternatives is not.
- [ ] **Is mutual exclusivity demonstrated, not assumed?** If roles are claimed to be distinct, show the discrimination evidence. What behaviours distinguish Coach from Advisor? If two roles can't be reliably distinguished by coders, they should merge.

---

## 4. Writing Quality

- [ ] **One idea per paragraph.** If a paragraph contains two claims, split it. If it contains zero claims (pure scene-setting), cut it.
- [ ] **No hedge stacking.** "This may potentially suggest a possible..." — pick a strength of claim and commit. Hedging is appropriate for empirical uncertainty, not for your own framework's design decisions.
- [ ] **No rhetorical inflation.** Words that signal inflation: "urgent," "critical gap," "paradigm shift," "transformative." If the contribution is real, it doesn't need these. Let the work speak.
- [ ] **Active voice for claims, passive for methods.** "AROMA separates support type from care role" (active — you're making a claim). "Papers were screened by two reviewers" (passive — you're reporting procedure). Don't hide claims in passive voice.
- [ ] **Cut "In this paper, we..."** The reader knows they're reading your paper. Start with the claim, not the meta-announcement.
- [ ] **Every sentence must survive the "so what?" test.** Read each sentence and ask: if I deleted this, would the argument collapse? If not, delete it.
- [ ] **Consistent terminology.** Don't alternate between "care role" and "relational stance" and "role identity" for the same concept unless you've defined each as distinct. Terminological drift in a taxonomy paper is fatal.

---

## 5. Figures and Tables

- [ ] **Does every figure earn its page space?** A figure that restates text is wasted space. A figure should reveal structure that prose cannot (relationships, distributions, flows).
- [ ] **Are tables self-contained?** A reader should understand a table without reading the surrounding text. Column headers must be unambiguous. Include a descriptive caption.
- [ ] **Is there a framework overview figure?** For taxonomy papers, a single figure showing the dimensional structure and relationships is expected. If it's missing, reviewers will note it.

---

## 6. Common CHI Rejection Patterns

### "This is a literature review, not a contribution"
**Trigger:** Paper surveys existing work and organizes it into categories without producing new analytical leverage. **Fix:** Show what the taxonomy predicts, explains, or enables that was previously invisible.

### "The framework is not validated"
**Trigger:** Taxonomy is derived top-down but presented as a finished result without empirical grounding. **Fix:** Be honest about what's validated and what's hypothesized. Partial validation (corpus grounding without human coding) is acceptable if clearly stated.

### "Overclaiming"
**Trigger:** Paper claims clinical implications without clinical evidence. **Fix:** Scope claims precisely. "AROMA predicts which role configurations are structurally paradoxical" is defensible. "AROMA improves mental health outcomes" is not.

### "No evaluation"
**Trigger:** No inter-rater reliability, no user study, no classifier performance. **Fix:** For CHI 2027, at minimum: human coding with kappa, expert validation, and ideally classifier evaluation. If phases are incomplete, frame the paper around what's done and what's planned.

### "Missing related work"
**Trigger:** Reviewer knows a paper the authors didn't cite. **Fix:** Related work must be exhaustive for the core claim. Search specifically for competing taxonomies, competing frameworks, and competing definitions of each key term.

### "Why is this not just [existing framework]?"
**Trigger:** Paper doesn't sufficiently differentiate from Cutrona & Suhr, or from Sharma et al., or from ESConv. **Fix:** For every framework you build on, state explicitly: "X provides [this]. X does not provide [that]. AROMA adds [this specific thing]."

---

## 7. Self-Review Protocol

Before considering any AROMA document "done":

1. **Read it as a hostile reviewer.** Find the weakest sentence and ask: would I accept this if someone else wrote it?
2. **Check every citation.** Does the cited source actually support the claim? Is the claim a fair representation or an overextension?
3. **Check cross-document consistency.** Do role counts, dimension definitions, and terminology match across all documents?
4. **Run the "so what?" pass.** Delete every sentence that doesn't advance an argument. If the document gets shorter by >20%, it was bloated.
5. **Run the terminology pass.** Ctrl+F every key term. Is it used consistently? Is it defined on first use?
6. **Check for circular reasoning.** The taxonomy cannot validate itself. "The roles are distinct because we defined them as distinct" is circular. The evidence must be external (corpus, coders, experts).
