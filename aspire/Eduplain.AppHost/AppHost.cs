using System.Globalization;
using Aspire.Hosting.ApplicationModel;

var builder = DistributedApplication.CreateBuilder(args);

var repositoryRoot = Path.GetFullPath(Path.Combine(builder.AppHostDirectory, "..", ".."));
var localEnv = LoadLocalEnv(repositoryRoot);

var djangoPort = GetIntSetting(localEnv, "ASPIRE_DJANGO_PORT", 8000);
var postgresPort = GetIntSetting(localEnv, "ASPIRE_POSTGRES_PORT", 55433);
var postgresDatabase = GetSetting(localEnv, "POSTGRES_DB", "academic_db");
var djangoSettingsModule = GetSetting(
    localEnv,
    "DJANGO_SETTINGS_MODULE",
    "config.settings.development"
);
var djangoEnvironment = GetSetting(localEnv, "DJANGO_ENVIRONMENT", "development");

var postgresUser = builder.AddParameter(
    "postgres-user",
    GetSetting(localEnv, "POSTGRES_USER", "academic_user"),
    publishValueAsDefault: false
);
var postgresPassword = builder.AddParameter(
    "postgres-password",
    GetRequiredSetting(localEnv, "POSTGRES_PASSWORD"),
    publishValueAsDefault: false,
    secret: true
);

var postgres = builder
    .AddPostgres("postgres", postgresUser, postgresPassword, port: postgresPort)
    .WithImageTag("17-alpine")
    .WithDataVolume("eduplain-aspire-postgres-data");

var database = postgres.AddDatabase("academic-db", postgresDatabase);
var python = ResolvePythonCommand(repositoryRoot);

var migrate = builder.AddExecutable(
    "django-migrate",
    python,
    repositoryRoot,
    "manage.py",
    "migrate",
    "--noinput"
);
ConfigureDjango(migrate).WaitFor(database);

var bootstrap = builder.AddExecutable(
    "django-bootstrap",
    python,
    repositoryRoot,
    "manage.py",
    "bootstrap_superuser",
    "--skip-if-unconfigured"
);
ConfigureDjango(bootstrap).WaitForCompletion(migrate);

var api = builder.AddExecutable(
    "django-api",
    python,
    repositoryRoot,
    "manage.py",
    "runserver",
    $"127.0.0.1:{djangoPort.ToString(CultureInfo.InvariantCulture)}"
);

ConfigureDjango(api)
    .WithHttpEndpoint(port: djangoPort, targetPort: djangoPort, isProxied: false)
    .WithHttpHealthCheck("/api/health/")
    .WaitForCompletion(migrate)
    .WaitForCompletion(bootstrap);

builder.Build().Run();

IResourceBuilder<ExecutableResource> ConfigureDjango(
    IResourceBuilder<ExecutableResource> resource
) => resource
    .WithEnvironment("DJANGO_SETTINGS_MODULE", djangoSettingsModule)
    .WithEnvironment("DJANGO_ENVIRONMENT", djangoEnvironment)
    .WithEnvironment("POSTGRES_DB", postgresDatabase)
    .WithEnvironment("POSTGRES_USER", postgresUser)
    .WithEnvironment("POSTGRES_PASSWORD", postgresPassword)
    .WithEnvironment("POSTGRES_HOST", "localhost")
    .WithEnvironment("POSTGRES_PORT", postgresPort.ToString(CultureInfo.InvariantCulture));

static string ResolvePythonCommand(string repositoryRoot)
{
    var windowsVenvPython = Path.Combine(repositoryRoot, ".venv", "Scripts", "python.exe");
    if (File.Exists(windowsVenvPython))
    {
        return windowsVenvPython;
    }

    var unixVenvPython = Path.Combine(repositoryRoot, ".venv", "bin", "python");
    return File.Exists(unixVenvPython) ? unixVenvPython : "python";
}

static int GetIntSetting(
    IReadOnlyDictionary<string, string> localEnv,
    string name,
    int defaultValue
)
{
    var rawValue = GetSetting(localEnv, name, defaultValue.ToString(CultureInfo.InvariantCulture));
    if (int.TryParse(rawValue, NumberStyles.None, CultureInfo.InvariantCulture, out var value))
    {
        return value;
    }

    throw new InvalidOperationException($"{name} must be an integer value.");
}

static string GetRequiredSetting(IReadOnlyDictionary<string, string> localEnv, string name)
{
    var value = GetSetting(localEnv, name, defaultValue: null);
    if (!string.IsNullOrWhiteSpace(value))
    {
        return value;
    }

    throw new InvalidOperationException($"Required setting {name} was not found.");
}

static string GetSetting(
    IReadOnlyDictionary<string, string> localEnv,
    string name,
    string? defaultValue
)
{
    var processValue = Environment.GetEnvironmentVariable(name);
    if (!string.IsNullOrWhiteSpace(processValue))
    {
        return processValue;
    }

    if (localEnv.TryGetValue(name, out var localValue) && !string.IsNullOrWhiteSpace(localValue))
    {
        return localValue;
    }

    return defaultValue ?? string.Empty;
}

static Dictionary<string, string> LoadLocalEnv(string repositoryRoot)
{
    var values = new Dictionary<string, string>(StringComparer.Ordinal);
    foreach (var fileName in new[] { ".env", ".env.local" })
    {
        var path = Path.Combine(repositoryRoot, fileName);
        if (!File.Exists(path))
        {
            continue;
        }

        foreach (var rawLine in File.ReadAllLines(path))
        {
            var line = rawLine.Trim();
            if (line.Length == 0 || line.StartsWith('#'))
            {
                continue;
            }

            var separator = line.IndexOf('=');
            if (separator <= 0)
            {
                continue;
            }

            var key = line[..separator].Trim();
            var value = line[(separator + 1)..].Trim();
            values[key] = Unquote(value);
        }
    }

    return values;
}

static string Unquote(string value)
{
    if (value.Length >= 2)
    {
        var quote = value[0];
        if ((quote == '"' || quote == '\'') && value[^1] == quote)
        {
            return value[1..^1];
        }
    }

    return value;
}
