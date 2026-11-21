# Steam update unblock on unsupported build — plan

**Goal:** When a startup pattern prewarm finds no LumaCore pattern for the
installed Steam build and Steam auto-updates are blocked, re-enable updates and
prompt once.

**Architecture:** `_download_pattern_body` distinguishes 404 ("absent") from
network failures ("error"). `prewarm_pattern_cache_if_missing` reports the set
of modules whose pattern was absent. `Main_gui.py` passes that to a new
`SFFMainWindow.offer_steam_update_for_unsupported_build()`, which unblocks only
when both `steamclient` and `steamui` are absent and `steam.cfg` says blocked.

**Spec:** this file (short design approved in chat).

## Global constraints

- Offline/failed downloads never unblock updates — only a 404.
- Never touch a `steam.cfg` that is not blocked.
- `steam.cfg` writes preserve unrelated lines.
- New source files carry the GPL header.

## Tasks

### Task 1: steam_updates helpers

**Files:** modify `sff/quick_tools/steam_updates.py`; test `tests/test_steam_updates.py`.

- [ ] `get_state(steam_path) -> str`: `"blocked" | "unblocked" | "unknown"` from the
      `BootStrapperInhibitAll` line.
- [ ] `_set_inhibit(steam_path, value)` rewrites that line only; `block_updates`
      passes `Enable`, `unblock_updates` passes `False`.
- [ ] Test: block then unblock keeps a `[other]` line; `get_state` returns
      `unblocked`; missing file returns `unknown`.

### Task 2: pattern prewarm reports absent builds

**Files:** modify `sff/lumacore/lumacore_setup.py`.

- [ ] `_download_pattern_body` returns `(body, reason)`, reason in
      `"ok" | "absent" | "error"` (404 = absent).
- [ ] `_prewarm_lumacore_patterns` returns `(all_ready, wrote, absent_labels)`.
- [ ] `prewarm_pattern_cache_if_missing` returns the same triple.

### Task 3: startup hook + prompt

**Files:** modify `Main_gui.py`, `sff/gui/main_window.py`.

- [ ] Unpack the triple in `_prewarm_luma`.
- [ ] Call `window.offer_steam_update_for_unsupported_build()` when both
      `steamclient` and `steamui` are absent.
- [ ] Method: return unless `get_state == "blocked"`; unblock; yes/no dialog
      ("Steam update required"); Yes → `bridge.restart_steam()`.
      Unblocking flips the state, so it prompts at most once per block.

### Task 4: changelog

- [ ] `CHANGELOG.md` Unreleased → Fixed.
