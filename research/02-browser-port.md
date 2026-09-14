# Case: porting a model into a browser

**Work:** adapting an existing PyTorch/CUDA image-inpainting model to ONNX and a WebGPU application. **When:** June 22, 2026. **Evidence:** developer account, public conversation export, working-project source, lab notes, and a deployment-related patch. Browser inference was **not rerun** in this review. [Sources](sources.md#moebius)

## Starting conditions mattered

Simon Willison was already working on Datasette while an agent handled changes that sometimes took several minutes. He used the waiting time for an exploratory side project: could the Moebius model run in a browser?

He did not start with only “build this.” He first asked a conversational model to inspect the upstream repository, find the weights, identify runtime requirements, and consider browser feasibility. Then he assembled local copies of the model code, weights, ONNX Runtime, and Transformers.js. The coding agent received a saved research note and a clear target: ONNX/WebGPU, a simple UI, and a specific working directory.

He asked it to commit frequently and maintain a plan and discovery notes. Those artifacts are public, but their existence alone does not prove that the documents improved performance.

## The observed feedback sequence

| Boundary | What the agent could check | What still happened |
|---|---|---|
| Original model → ONNX | Run reference inference; compare component outputs using identical tensors | Agent notes report parity checks, not just successful export. |
| Python pipeline → TypeScript | Compare the port with saved reference fixtures in Node | These checks did not establish that GPU execution worked in a browser. |
| Application → actual browser | The agent could serve files, but could not use its intended browser session | The human opened the app and returned errors/screenshots. |
| Chrome → Safari | Earlier checks did not cover Safari’s shader compiler | Safari rejected generated code for a 3D convolution. |
| Local app → deployed service | Files and weights were reachable | Reloading repeatedly downloaded about 1.3 GB of weights. |

The public transcript index records the crucial turns, not just the success story:

- **Turn 27:** the human clarifies that the failure occurred in Safari. The agent replaces a particular depth-one 3D convolution with a 2D equivalent and reports numerical comparisons after re-export.
- **Turn 28:** the human says it works and authorizes publishing to GitHub.
- **Turns 29–33:** the human reports repeated downloads and supplies a local copy of another working project as a reference. A subagent examines it.
- **Turn 34:** the human rejects automatic downloading on page load and specifies that downloading must wait for an explicitly labeled button click.

The [cache patch](https://github.com/simonw/moebius-web/commit/05c1cbc4894460a70a8bc1718ac6d152219e0f28) corroborates the last two changes: a Cache Storage module keyed by the stable model URL, removal of background prefetch, and revised button text. This review inspected that code; it did not independently verify every explanation the agent gave for HTTP caching behavior.

## What made progress possible

**Observed:** reference implementations and real dependencies were locally available. The developer supplied concrete failing observations, deployment targets, and an example of already-working caching behavior. Different checks addressed different boundaries.

**Interpretation:** the productive unit here was not “generate the application.” It was repeatedly narrowing a mismatch: reference versus port, Node versus browser, one browser versus another, local serving versus deployment. A passing check at one boundary did not validate the next.

The human’s instruction about download timing is also a concrete example of product judgment remaining human-owned. Functional code that downloads early is not equivalent to the experience the human wants.

## Costs and limits that the demo hides

Willison explicitly says he did not inspect the implementation code during this project and learned little about the underlying technologies from producing it. He subsequently sought an explanation. The case therefore does **not** demonstrate preserved implementation understanding.

The project needed roughly 1.24 GB of converted weights, a compatible GPU/browser, publication credentials, repeated browser testing, and model re-exports. Credentials were granted for publishing; this review does not recommend copying the token-handling arrangement described in the account.

No complete human-time or compute-cost accounting is published in the inspected materials. Parallel work on Datasette prevents interpreting transcript duration as exclusive effort on the port. “Completed in a day” is not a measured speedup.

## Applicability—and limits

**Useful when:** porting or integrating a component with a runnable reference; building browser/native clients whose deployment environment differs from development.

**Requires:** representative inputs, a way to compare behavior, and access to the real target environment. Someone must still decide whether numerical differences and product behavior are acceptable.

**Does not establish:** that an apparently working port is production-ready, that headless parity tests replace device testing, or that low code-review involvement is appropriate for higher-risk software. This was explicitly an exploratory application, not a demonstrated no-compromise development process.
