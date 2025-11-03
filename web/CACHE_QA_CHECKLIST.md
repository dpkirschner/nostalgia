# Client-Side Caching & SWR - QA Validation Checklist

## Overview

This document provides step-by-step testing scenarios for the client-side caching and SWR implementation.

**Cache Configuration:**
- BBox stale time: 60 seconds
- Location detail stale time: 15 minutes
- BBox LRU limit: 3 entries
- Persisted cache: IndexedDB with 24-hour max age

---

## Dev Tools Setup

Before starting QA, open the browser console and run:

```javascript
cache.help()    // View available cache inspector commands
cache.stats()   // View current cache statistics
```

---

## Test Scenarios

### ✅ Scenario 1: BBox Revisit Within 60s

**Goal:** Pins render instantly from cache, then silently update if data changed

**Steps:**
1. Open the app and pan/zoom to a specific region
2. Wait for pins to load
3. Note the number of pins displayed
4. Pan to a different region
5. **Within 60 seconds**, pan back to the original region
6. Observe pins render immediately
7. Open console and run `cache.stats()` to verify cache hit

**Expected:**
- ✅ Pins appear instantly (< 100ms)
- ✅ No skeleton/loading state
- ✅ Console shows cache hit log
- ✅ Background refresh may occur silently

---

### ✅ Scenario 2: LRU Eviction (3 Regions)

**Goal:** Fourth region evicts the oldest; returning to oldest triggers fresh fetch

**Steps:**
1. Clear cache: `cache.clear()`
2. Visit Region A, wait for pins to load
3. Visit Region B, wait for pins to load
4. Visit Region C, wait for pins to load
5. Run `cache.bbox()` to verify 3 entries
6. Visit Region D (fourth region)
7. Run `cache.bbox()` again to verify Region A was evicted
8. Return to Region A
9. Observe network request in Network tab

**Expected:**
- ✅ After visiting 3 regions, `cache.bbox()` shows 3 entries
- ✅ After visiting 4th region, oldest (Region A) is evicted
- ✅ Returning to Region A triggers network fetch (no instant cache)
- ✅ Console shows "EVICTED" log with reason: "LRU"

---

### ✅ Scenario 3: Pin Tapped Twice Within 15m

**Goal:** Second tap shows instant detail (no loader)

**Steps:**
1. Tap a pin on the map
2. Wait for location detail timeline to load
3. Close the drawer
4. **Within 15 minutes**, tap the same pin again
5. Observe detail appears instantly

**Expected:**
- ✅ Detail drawer opens instantly (< 100ms)
- ✅ No skeleton/loading state
- ✅ Timeline entries visible immediately
- ✅ Background refresh may occur (subtle "Refreshing..." indicator)

---

### ✅ Scenario 4: Detail Stale (>15m)

**Goal:** Old detail shows immediately; background refresh replaces it when done

**Steps:**
1. Tap a pin and view detail
2. **Simulate stale data** by manually setting stale time to 0:
   ```javascript
   // In browser console:
   cache.clear()
   ```
3. Wait 1 second (cache now stale)
4. Tap the pin again
5. Observe behavior

**Expected:**
- ✅ Cached detail shows immediately (if available)
- ✅ "Refreshing..." indicator appears at top of timeline
- ✅ When refresh completes, indicator disappears
- ✅ Timeline updates if data changed

**Note:** Since we can't easily wait 15 minutes in QA, clearing cache simulates staleness.

---

### ✅ Scenario 5: Memory Submission

**Goal:** Reopening the same location triggers fresh fetch; cached version isn't shown as final

**Steps:**
1. Tap a pin and view detail
2. Click "Add what you remember"
3. Submit a memory
4. Close the drawer
5. **Immediately** tap the same pin again
6. Observe detail is refreshed

**Expected:**
- ✅ Cache is invalidated after memory submission
- ✅ Detail drawer shows loading state briefly
- ✅ Fresh data is fetched from server
- ✅ Console shows cache invalidation log

---

### ✅ Scenario 6: Rapid Pan

**Goal:** Only final bbox request resolves; earlier ones aborted; no flicker

**Steps:**
1. Rapidly pan the map back and forth (swipe gesture on mobile, click-drag on desktop)
2. Observe pin rendering behavior
3. Check Network tab for aborted requests

**Expected:**
- ✅ No flickering of pins
- ✅ Network tab shows earlier requests cancelled/aborted
- ✅ Only the final bbox query completes
- ✅ Pins render for the final viewport position

---

### ✅ Scenario 7: 429 Rate Limit

**Goal:** Cached content remains; refresh retries once after Retry-After

**Steps:**
1. **Simulate 429** by modifying API response (requires backend mock or browser dev tools)
2. Trigger a detail refresh (e.g., re-tap a pin)
3. Observe behavior

**Expected:**
- ✅ Cached detail remains visible
- ✅ No error UI shown to user
- ✅ Refresh retries automatically after `retryAfterMs`
- ✅ Console logs retry attempt

**Note:** This scenario requires API mocking and is optional for initial QA.

---

### ✅ Scenario 8: Offline Mode

**Goal:** Cached content shows; no crashes; clear "offline" hint

**Steps:**
1. Visit a few locations to populate cache
2. Open Chrome DevTools → Network tab → Enable "Offline" mode
3. Pan the map to a new region
4. Tap a cached pin
5. Observe behavior

**Expected:**
- ✅ App doesn't crash
- ✅ Cached pins remain visible
- ✅ Cached detail shows if available
- ✅ Error toast appears for network failures
- ✅ No white screen or broken UI

---

## Cache Persistence Testing

### ✅ Scenario 9: Page Refresh

**Goal:** Cache survives page refresh (IndexedDB persistence)

**Steps:**
1. Visit a few locations to populate cache
2. Run `cache.stats()` and note "Persisted Cache" item count
3. Refresh the page (Cmd+R / Ctrl+R)
4. Run `cache.stats()` again
5. Tap a previously viewed pin

**Expected:**
- ✅ `cache.stats()` shows same persisted cache count after refresh
- ✅ Tapping a cached pin shows instant detail
- ✅ No network requests for cached data (check Network tab)

---

### ✅ Scenario 10: Cache Size Limit

**Goal:** Persisted cache doesn't exceed reasonable size

**Steps:**
1. Visit 10+ different locations
2. Run `cache.stats()`
3. Note "Size (KB)" in persisted cache section

**Expected:**
- ✅ Cache size < 1MB (reasonable for ~10 locations)
- ✅ No browser storage quota errors

---

## Dev Inspector Validation

### ✅ Scenario 11: Cache Inspector Commands

**Goal:** All dev inspector commands work correctly

**Steps:**
1. Open browser console
2. Run each command:
   ```javascript
   cache.help()      // Shows help message
   cache.stats()     // Shows statistics
   cache.queries()   // Lists all queries
   cache.bbox()      // Shows bbox cache
   cache.events()    // Shows event log
   cache.clear()     // Clears all caches
   ```

**Expected:**
- ✅ All commands execute without errors
- ✅ Output is formatted and readable
- ✅ `cache.clear()` successfully clears all caches

---

### ✅ Scenario 12: Cache Event Logging

**Goal:** Cache events are logged in dev mode

**Steps:**
1. Clear cache: `cache.clear()`
2. Pan to a new region
3. Tap a pin
4. Run `cache.events()`

**Expected:**
- ✅ Events include: `cache_miss`, `cache_hit`, `swr_refresh_started`, `swr_refresh_succeeded`
- ✅ Events are color-coded in console
- ✅ Event table shows meaningful data

---

## Integration Tests

### ✅ Scenario 13: Map Source Updates

**Goal:** Map layer doesn't re-create sources/layers on every cache update

**Steps:**
1. Open React DevTools
2. Pan the map to trigger bbox query
3. Return to a cached region
4. Observe MapCanvas component re-renders

**Expected:**
- ✅ MapCanvas doesn't unmount/remount
- ✅ Map source data is updated in place
- ✅ No visual flicker or map reset

---

### ✅ Scenario 14: Drawer SWR Updates

**Goal:** Drawer subscribes to location updates while open; unsubscribes on close

**Steps:**
1. Tap a pin to open detail drawer
2. Observe "Refreshing..." indicator if data is stale
3. Close the drawer
4. Reopen the same pin
5. Observe no duplicate network requests

**Expected:**
- ✅ Drawer shows refresh indicator when fetching
- ✅ Background refresh completes silently
- ✅ Closing drawer doesn't cancel in-flight requests
- ✅ Reopening drawer uses cached data

---

## Performance Benchmarks

### ✅ Scenario 15: Cache Hit Performance

**Goal:** Cached data renders < 100ms

**Steps:**
1. Clear cache: `cache.clear()`
2. Visit a location and wait for data to load
3. Close the drawer
4. **Immediately** tap the same pin again
5. Use Chrome DevTools Performance tab to measure time to render

**Expected:**
- ✅ Detail drawer opens < 100ms
- ✅ No network requests
- ✅ User perceives instant response

---

## Cleanup & Reporting

### Final Steps

1. Run `cache.stats()` one last time
2. Take a screenshot of the output
3. Document any issues found
4. Clear all caches: `cache.clear()`

---

## Success Criteria

✅ All scenarios pass without errors
✅ No console errors during testing
✅ Cache persistence works across page refreshes
✅ LRU eviction functions correctly
✅ SWR provides instant cached responses
✅ Background refreshes are silent and non-blocking
✅ Dev inspector provides useful debugging info

---

## Known Limitations

1. **Offline support**: Basic (shows cached data, but no service worker for offline-first)
2. **Cache size**: No hard limit enforced (relies on browser storage quota)
3. **Prefetching**: Not implemented in this phase
4. **Retry logic**: Respects Retry-After header, but no exponential backoff cap

---

## Next Steps

After passing all scenarios:

1. **Performance monitoring**: Add telemetry for cache hit/miss rates
2. **Prefetching**: Implement hover and adjacent tile prefetching
3. **Service Worker**: Add offline-first architecture with background sync
4. **Cache analytics**: Track staleness vs freshness ratios in production
