interface ResearchSettingsProps {
  onChange: () => void;
}

export default function ResearchSettings({ onChange }: ResearchSettingsProps) {
  return (
    <div className="space-y-6">
      <div className="card p-6">
        <h2 className="text-lg font-semibold mb-4">Research Sources</h2>
        <p className="text-muted-foreground mb-6">
          Configure which research sources to use and their priority order.
        </p>

        <div className="space-y-4">
          {[
            { name: "Web Search", providers: ["DuckDuckGo", "SerpApi (Google)", "Bing"] },
            { name: "Academic Research", providers: ["arXiv"] },
            { name: "Code Analysis", providers: ["GitHub"] },
            { name: "Creative Writing", providers: ["TV Tropes"] },
          ].map((source) => (
            <div
              key={source.name}
              className="flex items-center justify-between p-4 border border-border rounded-md"
            >
              <div>
                <div className="font-medium">{source.name}</div>
                <div className="text-sm text-muted-foreground">{source.providers.join(", ")}</div>
              </div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  defaultChecked
                  onChange={onChange}
                  className="rounded border-border"
                />
              </label>
            </div>
          ))}
        </div>
      </div>

      <div className="card p-6">
        <h2 className="text-lg font-semibold mb-4">Research Limits</h2>

        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="label">Max Results per Source</label>
            <input
              type="number"
              defaultValue="50"
              min="1"
              max="200"
              className="input w-full"
              onChange={onChange}
            />
          </div>

          <div>
            <label className="label">Research Timeout (seconds)</label>
            <input
              type="number"
              defaultValue="30"
              min="5"
              max="120"
              className="input w-full"
              onChange={onChange}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
