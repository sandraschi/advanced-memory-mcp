interface ExportSettingsProps {
  onChange: () => void;
}

export default function ExportSettings({ onChange }: ExportSettingsProps) {
  return (
    <div className="space-y-6">
      <div className="card p-6">
        <h2 className="text-lg font-semibold mb-4">Export Formats</h2>
        <p className="text-muted-foreground mb-6">
          Choose which export formats to enable and configure default settings.
        </p>

        <div className="space-y-4">
          {[
            { name: "PDF Export", description: "Generate PDF documents with tables of contents" },
            { name: "HTML Export", description: "Create interactive HTML documentation" },
            { name: "Docsify Export", description: "Generate searchable documentation sites" },
            { name: "Claude Skills", description: "Export knowledge as reusable AI skills" },
            { name: "Pandoc Export", description: "Convert to DOCX, EPUB, and other formats" },
          ].map((format) => (
            <div
              key={format.name}
              className="flex items-center justify-between p-4 border border-border rounded-md"
            >
              <div>
                <div className="font-medium">{format.name}</div>
                <div className="text-sm text-muted-foreground">{format.description}</div>
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
        <h2 className="text-lg font-semibold mb-4">Default Export Location</h2>

        <div className="space-y-4">
          <div>
            <label className="label">Base Directory</label>
            <input
              type="text"
              defaultValue="~/Desktop/advanced-memory-exports"
              className="input w-full"
              onChange={onChange}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Where to save exported files. Use ~ for home directory.
            </p>
          </div>

          <div>
            <label className="label">File Naming Pattern</label>
            <input
              type="text"
              defaultValue="{project}-{timestamp}"
              className="input w-full"
              onChange={onChange}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Variables: {`{project}`}, {`{timestamp}`}, {`{format}`}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
