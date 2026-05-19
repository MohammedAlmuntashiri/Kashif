// Helpers for Saudi market hours + relative time formatting.
//
// Tadawul trading hours: Sunday-Thursday, 10:00-15:00 Asia/Riyadh.
// All computation happens client-side using Intl.DateTimeFormat so we
// don't need a round-trip just to know whether the market is open.

const TRADING_DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu'];
const OPEN_HOUR = 10;
const CLOSE_HOUR = 15;

// Read current time as if we were in Asia/Riyadh — works in any browser
// regardless of the user's actual timezone.
function _riyadhParts(now = new Date()) {
  const fmt = new Intl.DateTimeFormat('en-US', {
    timeZone: 'Asia/Riyadh',
    weekday: 'short',
    hour: 'numeric',
    minute: 'numeric',
    hour12: false,
  });
  const parts = fmt.formatToParts(now);
  const get = (type) => parts.find((p) => p.type === type)?.value;
  return {
    weekday: get('weekday'),
    hour:    parseInt(get('hour'), 10),
    minute:  parseInt(get('minute'), 10),
  };
}

/**
 * Returns one of: 'open' | 'pre_open' | 'closed_today' | 'closed_weekend'.
 * `nextOpenDay`: 'today' | 'tomorrow' | 'sunday'. Useful for messaging.
 */
export function getMarketStatus(now = new Date()) {
  const { weekday, hour } = _riyadhParts(now);
  const isTradingDay = TRADING_DAYS.includes(weekday);

  if (isTradingDay) {
    if (hour < OPEN_HOUR)   return { status: 'pre_open',     nextOpenDay: 'today' };
    if (hour < CLOSE_HOUR)  return { status: 'open',         nextOpenDay: null };
    // Post-close on a trading day. If today is Thursday, next open is Sunday.
    return {
      status: 'closed_today',
      nextOpenDay: weekday === 'Thu' ? 'sunday' : 'tomorrow',
    };
  }
  // Weekend (Fri / Sat). Next open is Sunday morning.
  return { status: 'closed_weekend', nextOpenDay: 'sunday' };
}

/**
 * Returns a translation key + interpolation args for "N min/hr/days ago".
 * Caller uses t(result.key, result.args) to render.
 */
export function formatTimeAgo(isoOrDate) {
  if (!isoOrDate) return null;
  const then = isoOrDate instanceof Date ? isoOrDate : new Date(isoOrDate);
  if (isNaN(then.getTime())) return null;
  const diffSec = Math.max(0, Math.floor((Date.now() - then.getTime()) / 1000));
  if (diffSec < 60)        return { key: 'time.justNow', args: {} };
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60)        return { key: 'time.minAgo', args: { n: diffMin } };
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24)         return { key: 'time.hrAgo', args: { n: diffHr } };
  const diffDay = Math.floor(diffHr / 24);
  return { key: 'time.dayAgo', args: { n: diffDay } };
}
