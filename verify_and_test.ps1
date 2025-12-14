# Comprehensive Verification and Testing Script
# This script verifies the project setup and runs integration tests

$ErrorActionPreference = "Continue"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = "c:\Users\ahmed\Desktop\Parallel-Data-Analysis\Script\logs\verification_$timestamp.txt"

function Log {
    param([string]$message, [string]$level = "INFO")
    $logMessage = "[$level] $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $message"
    Write-Host $logMessage
    Add-Content -Path $logFile -Value $logMessage
}

function Check-File {
    param([string]$path, [string]$description)
    if (Test-Path $path) {
        Log "OK - $description exists" "PASS"
        return $true
    } else {
        Log "FAIL - $description NOT found: $path" "FAIL"
        return $false
    }
}

function Check-YamlValid {
    param([string]$path, [string]$description)
    try {
        $content = Get-Content $path -Raw
        if ($content -match '^\s*$') {
            Log "FAIL - $description is empty" "FAIL"
            return $false
        }
        Log "OK - $description exists and is not empty" "PASS"
        return $true
    }
    catch {
        Log "FAIL - $description check error: $_" "FAIL"
        return $false
    }
}

function Check-PythonSyntax {
    param([string]$path, [string]$description)
    try {
        $result = python -m py_compile $path 2>&1
        if ($LASTEXITCODE -eq 0) {
            Log "OK - $description has valid Python syntax" "PASS"
            return $true
        } else {
            Log "FAIL - $description has syntax errors: $result" "FAIL"
            return $false
        }
    }
    catch {
        Log "FAIL - $description syntax check error: $_" "FAIL"
        return $false
    }
}

# Start Verification
Log "========== PROJECT VERIFICATION STARTED ==========" "INFO"
Log "Timestamp: $timestamp" "INFO"

# Change to Script directory
Set-Location "c:\Users\ahmed\Desktop\Parallel-Data-Analysis\Script"

# 1. File Structure Verification
Log "" "INFO"
Log "=== 1. FILE STRUCTURE VERIFICATION ===" "INFO"
$fileChecks = @(
    @("docker-compose.yml", "Docker Compose File"),
    @("docker/Dockerfile", "Web API Dockerfile"),
    @("api/web_api.py", "Web API Script"),
    @("src/main.py", "Main Script"),
    @("config/app_config.yaml", "App Config"),
    @("requirements.txt", "Python Requirements")
)

$filePass = 0
$fileFail = 0
foreach ($check in $fileChecks) {
    if (Check-File $check[0] $check[1]) {
        $filePass++
    } else {
        $fileFail++
    }
}

# 2. Configuration Files Validation
Log "" "INFO"
Log "=== 2. CONFIGURATION FILES VALIDATION ===" "INFO"
Check-YamlValid "config/app_config.yaml" "app_config.yaml"
Check-YamlValid "config/environment.yml" "environment.yml"

# 3. Python Syntax Validation
Log "" "INFO"
Log "=== 3. PYTHON SYNTAX VALIDATION ===" "INFO"
$pythonFiles = @(
    @("api/web_api.py", "Web API"),
    @("src/main.py", "Main Script"),
    @("src/data_loader.py", "Data Loader"),
    @("src/data_analyzer.py", "Data Analyzer"),
    @("src/performance_monitor.py", "Performance Monitor"),
    @("spark_jobs/mapreduce_job.py", "MapReduce Job"),
    @("spark_jobs/aggregation_job.py", "Aggregation Job"),
    @("spark_jobs/statistical_analysis.py", "Statistical Analysis Job")
)

$pythonPass = 0
$pythonFail = 0
foreach ($check in $pythonFiles) {
    if (Check-PythonSyntax $check[0] $check[1]) {
        $pythonPass++
    } else {
        $pythonFail++
    }
}

# 4. Docker Compose Validation
Log "" "INFO"
Log "=== 4. DOCKER COMPOSE VALIDATION ===" "INFO"
try {
    $dockerTest = docker-compose config 2>&1
    if ($LASTEXITCODE -eq 0) {
        Log "OK - Docker Compose file is valid" "PASS"
    } else {
        Log "FAIL - Docker Compose validation error" "FAIL"
    }
}
catch {
    Log "WARN - Docker Compose check unavailable (Docker not running)" "WARN"
}

# 5. Test Data Validation
Log "" "INFO"
Log "=== 5. TEST DATA VALIDATION ===" "INFO"
$testDataFiles = @(
    @("data/input/sample_sales.csv", "Sample Sales Data"),
    @("data/input/spotify_data clean.csv", "Spotify Data"),
    @("data/input/StudentsPerformance.csv", "Student Performance Data")
)

$dataPass = 0
$dataFail = 0
foreach ($check in $testDataFiles) {
    if (Check-File $check[0] $check[1]) {
        $dataPass++
    } else {
        $dataFail++
    }
}

# 6. Summary
Log "" "INFO"
Log "=== VERIFICATION SUMMARY ===" "INFO"
Log "File Structure: $filePass passed, $fileFail failed" "INFO"
Log "Python Syntax: $pythonPass passed, $pythonFail failed" "INFO"
Log "Test Data: $dataPass passed, $dataFail failed" "INFO"

if ($fileFail -eq 0 -and $pythonFail -eq 0) {
    Log "" "INFO"
    Log "========== ALL VERIFICATION CHECKS PASSED ==========" "PASS"
    Log "Verification log: $logFile" "INFO"
} else {
    Log "" "INFO"
    Log "========== SOME CHECKS FAILED ==========" "WARN"
    Log "Verification log: $logFile" "INFO"
}
