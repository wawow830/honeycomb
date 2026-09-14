# Case: sixteen agents building a C compiler

**Work:** a new Rust implementation of a C compiler, exercised against existing software. **When:** reported February 5, 2026. **Evidence:** Anthropic’s first-person experiment report and a pinned public repository. The development harness and claimed benchmark results were **not reproduced** here. [Sources](sources.md#compiler)

## Human input and execution arrangement

Nicholas Carlini specified a dependency-free, GCC-compatible optimizing compiler, multiple backends, an SSA intermediate representation, and the ability to compile the Linux kernel. He supplied and continually improved the test environment.

The reported harness repeatedly launched agent sessions inside separate containers. Each cloned a shared Git repository, claimed a task through a file in `current_tasks/`, worked locally, integrated upstream changes, and pushed its work. There was **no manager agent** directing the overall plan. The public snapshot contains task-lock files describing specific outstanding defects.

This is already more specific than “a team of agents”: the units of coordination were task claims, isolated working copies, Git integration, and failing compiler cases.

## Where sixteen agents stopped helping

Initially, many independent failing tests supplied parallel work. Later, compiling Linux became one large blocked task: agents hit the same defect, fixed it, and overwrote one another’s changes. Agent count did not resolve the dependency.

Carlini reports changing the **test decomposition**, not simply the prompts. A new harness compiled most kernel files with GCC and selected subsets with the new compiler. By changing which files used the known-good compiler, agents could narrow failures to different subsets and work on distinct defects. Some failures involved pairs of files and needed further reduction.

**Interpretation:** the enabling change was making failures independently diagnosable. “Split the task among agents” would not have supplied that property by itself.

## Feedback engineering was substantial human work

The account describes:

- Selecting external compiler suites and writing real-project build/verifier scripts.
- Adding new tests when agents found ways to make the wrong kind of progress.
- Strengthening CI because new features repeatedly broke existing functionality.
- Saving detailed logs while giving agents concise, searchable failure summaries.
- Providing faster test subsets, stable within an agent’s environment, instead of rerunning everything for every change.

Stable samples make successive local results more comparable; they do not prove identical generations, complete coverage, or a deterministic end-to-end run.

## Reported result versus inspectable assurance

The author reports nearly 2,000 sessions over two weeks, approximately $20,000 in API cost, and a roughly 100,000-line compiler capable of compiling substantial existing projects. These are a vendor researcher’s reported outcomes, not a compute-matched comparison or a measured productivity multiplier.

The same report explicitly limits the achievement:

- The demonstrated x86 Linux build uses GCC for 16-bit boot code.
- The demonstration used external assembling/linking; emerging replacements were buggy.
- Generated programs were less efficient than GCC output even with GCC optimizations disabled.
- The implementation was not a general drop-in replacement, and code quality was below expert-written Rust.

The **published artifact itself demands skepticism**. At commit `6f1b99acb2f4ec2414592136c2009fe7713deec3`:

- A human-written README warning says the rest of the code/docs are agent-written, correctness has not been validated, and documentation may make false claims.
- The README describes an integration-test directory named `tests/`; the complete Git tree returned by GitHub contains **no such directory**.
- `Cargo.toml` exposes optional GCC fallback features. Their existence does not identify the build flags used for a demonstration.
- The pinned README claims standalone assembly/linking by default, while the publication says its demonstration used external tools. The former is explicitly unvalidated generated documentation; the latter describes a particular demonstrated build. Neither should silently substitute for the other.

This does not negate the artifact or establish that the reported builds failed. It means the public source snapshot is **not the full evidence needed to reproduce the headline**. Generated status documentation must not be promoted into independent validation.

## Applicability—and limits

**Useful when:** a rewrite, port, migration, or optimization has a runnable reference and many separable failing cases.

**Requires:** an authoritative behavioral comparison, useful failure localization, isolated work, integration checks, and enough resources to pay for concurrent attempts. Reference implementations can themselves have bugs or compatibility quirks; matching one is not equivalent to implementing every intended requirement.

**Does not establish:** that sixteen agents are efficient for ordinary features, that two weeks includes all human setup effort, or that large code volume implies maintainability. This was explicitly a capability stress test. Its most transferable observation is **how a human changed the feedback problem so parallel work became possible**, not the number of agents or the loop script.
