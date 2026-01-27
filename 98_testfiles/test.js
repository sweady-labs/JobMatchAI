// n8n Code node (no require)
// Extract the JSON content of .latest_job and return it directly.
const FALLBACK = [{ jobFilePath: '/workspace/jobs/candidates/example_user/0_inbox-jobs/2025-01-15' }];

function parseBinaryEntry(entry) {
  const payload = entry?.data ?? entry;
  if (!payload) {
    return null;
  }

  try {
    const raw = Buffer.from(payload, 'base64').toString('utf8');
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) {
      return parsed;
    }
    if (parsed?.jobFilePath) {
      return [parsed];
    }
  } catch (e) {
    // ignore parse errors
  }
  return null;
}

function parseLatestJob(binary) {
  if (!binary) {
    return null;
  }

  // Try the "data" key first (common when using default Read node)
  const primary = parseBinaryEntry(binary.data);
  if (primary) {
    return primary;
  }

  for (const key of Object.keys(binary)) {
    const parsed = parseBinaryEntry(binary[key]);
    if (parsed) {
      return parsed;
    }
  }
  return null;
}

const fromBinary = parseLatestJob($binary);
const directJson = Array.isArray($json)
  ? $json
  : $json?.jobFilePath
    ? [{ jobFilePath: $json.jobFilePath }]
    : null;

const latestJobs = fromBinary || directJson || FALLBACK;

return latestJobs.map((entry) => ({
  json: { jobFilePath: entry.jobFilePath },
}));
