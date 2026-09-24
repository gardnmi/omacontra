# Browser runtime notices

The original game, artwork credits, music credits, and attribution files remain
in `campaign/credits/THIRD_PARTY/`. The browser build also distributes these
unmodified runtime components:

- **Pyodide 314.0.7**, Mozilla Public License 2.0.
  Source (including build recipes): https://github.com/pyodide/pyodide/tree/314.0.7
  Corresponding license: `pyodide-LICENSE.txt`.
- **CPython 3.14.2**, included in that Pyodide distribution.
  Source and component notices: https://github.com/python/cpython/tree/v3.14.2
  Corresponding license and incorporated component notices: `python-LICENSE.txt`.
- **Emscripten 5.0.3** runtime, included in that Pyodide distribution.
  Source: https://github.com/emscripten-core/emscripten/tree/5.0.3
  Corresponding license: `emscripten-LICENSE.txt`.

The Pyodide JavaScript, WebAssembly binary, and Python standard-library archive
are copied without changes from the pinned npm distribution. These notices and
source links must remain with the deployed browser assets. The game's MIT
license does not replace the licenses of those components.
