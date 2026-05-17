// Tiny relative-time helper. Returns a localized "X minutes/hours/days ago"
// string. Uses Intl.RelativeTimeFormat so Arabic comes out naturally
// ("قبل ساعتين") without us shipping a dictionary.

export function timeAgo(iso, lang = 'en') {
  const date = new Date(iso);
  const diffSec = (date.getTime() - Date.now()) / 1000;   // negative for past
  const abs = Math.abs(diffSec);

  const rtf = new Intl.RelativeTimeFormat(lang, { numeric: 'auto' });

  if (abs < 60)         return rtf.format(Math.round(diffSec),        'second');
  if (abs < 3600)       return rtf.format(Math.round(diffSec / 60),   'minute');
  if (abs < 86_400)     return rtf.format(Math.round(diffSec / 3600), 'hour');
  if (abs < 2_592_000)  return rtf.format(Math.round(diffSec / 86_400), 'day');
  if (abs < 31_536_000) return rtf.format(Math.round(diffSec / 2_592_000), 'month');
  return rtf.format(Math.round(diffSec / 31_536_000), 'year');
}
