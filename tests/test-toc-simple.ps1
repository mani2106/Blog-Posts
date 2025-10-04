# Simple TOC Docker Testing Script
Write-Host "🧪 TOC Functionality Docker Tests" -ForegroundColor Green

$passed = 0
$failed = 0

function Test-Result {
    param($name, $condition, $details = "")
    if ($condition) {
        Write-Host "✅ $name" -ForegroundColor Green
        if ($details) { Write-Host "   $details" -ForegroundColor Gray }
        $script:passed++
    } else {
        Write-Host "❌ $name" -ForegroundColor Red
        if ($details) { Write-Host "   $details" -ForegroundColor Gray }
        $script:failed++
    }
}

# Test 1: Check Docker availability
Write-Host "`n📋 Environment Tests" -ForegroundColor Cyan
try {
    $dockerCheck = docker --version 2>$null
    Test-Result "Docker Available" ($LASTEXITCODE -eq 0) $dockerCheck
} catch {
    Test-Result "Docker Available" $false "Docker not found"
}

try {
    $composeCheck = docker-compose --version 2>$null
    Test-Result "Docker Compose Available" ($LASTEXITCODE -eq 0) $composeCheck
} catch {
    Test-Result "Docker Compose Available" $false "Docker Compose not found"
}

# Test 2: Start Jekyll container
Write-Host "`n📋 Container Tests" -ForegroundColor Cyan
Write-Host "🔨 Starting Jekyll container..." -ForegroundColor Yellow

try {
    # Clean up any existing containers
    docker-compose down 2>$null | Out-Null

    # Start Jekyll service
    $startResult = docker-compose up -d jekyll 2>&1
    Test-Result "Jekyll Container Start" ($LASTEXITCODE -eq 0) "Container started"

    if ($LASTEXITCODE -eq 0) {
        # Wait for Jekyll to be ready
        Write-Host "⏳ Waiting for Jekyll..." -ForegroundColor Yellow
        $ready = $false
        $attempts = 0
        $maxAttempts = 24  # 2 minutes with 5-second intervals

        while (-not $ready -and $attempts -lt $maxAttempts) {
            Start-Sleep -Seconds 5
            $attempts++

            try {
                $response = Invoke-WebRequest -Uri "http://localhost:4000" -TimeoutSec 3 -ErrorAction SilentlyContinue
                if ($response.StatusCode -eq 200) {
                    $ready = $true
                }
            } catch {
                # Continue waiting
            }

            if ($attempts % 4 -eq 0) {
                Write-Host "   Attempt $attempts/$maxAttempts..." -ForegroundColor Gray
            }
        }

        Test-Result "Jekyll Ready" $ready "Responded after $($attempts * 5) seconds"

        if ($ready) {
            # Test 3: TOC functionality tests
            Write-Host "`n📋 TOC Functionality Tests" -ForegroundColor Cyan

            # Test posts with different header structures
            $testCases = @(
                @{
                    Name = "Security Hardening Post"
                    Url = "http://localhost:4000/2025/09/30/jekyll-blog-security-hardening-journey.html"
                    ExpectTOC = $true
                },
                @{
                    Name = "Linear Regression Post"
                    Url = "http://localhost:4000/2020/08/31/linear-regression-grad-desc.html"
                    ExpectTOC = $true
                },
                @{
                    Name = "Model Agnostic Post"
                    Url = "http://localhost:4000/2021/05/29/model-agnostic-featimp.html"
                    ExpectTOC = $false
                }
            )

            foreach ($test in $testCases) {
                try {
                    $response = Invoke-WebRequest -Uri $test.Url -TimeoutSec 10 -ErrorAction SilentlyContinue

                    if ($response.StatusCode -eq 200) {
                        Test-Result "$($test.Name) - Page Load" $true "HTTP 200 OK"

                        $html = $response.Content

                        # Check for TOC container
                        $hasTOCContainer = $html -match 'class="toc-container"'
                        if ($test.ExpectTOC) {
                            Test-Result "$($test.Name) - TOC Container" $hasTOCContainer "TOC container found"
                        } else {
                            Test-Result "$($test.Name) - TOC Hidden" (-not $hasTOCContainer) "TOC correctly hidden"
                        }

                        # Check for ARIA attributes
                        $hasARIA = $html -match 'role="complementary"' -and $html -match 'aria-labelledby'
                        Test-Result "$($test.Name) - ARIA Attributes" $hasARIA "Accessibility attributes present"

                        # Check for TOC JavaScript
                        $hasJS = $html -match 'initializeTOC|generateFallbackTOC'
                        Test-Result "$($test.Name) - TOC JavaScript" $hasJS "TOC JavaScript found"

                    } else {
                        Test-Result "$($test.Name) - Page Load" $false "HTTP $($response.StatusCode)"
                    }
                } catch {
                    Test-Result "$($test.Name) - Page Load" $false "Error: $($_.Exception.Message)"
                }
            }

            # Test 4: CSS and responsive design
            Write-Host "`n📋 CSS and Responsive Tests" -ForegroundColor Cyan

            try {
                $cssResponse = Invoke-WebRequest -Uri "http://localhost:4000/assets/css/style.css" -TimeoutSec 10
                Test-Result "CSS Asset Loading" ($cssResponse.StatusCode -eq 200) "Main stylesheet loaded"

                if ($cssResponse.StatusCode -eq 200) {
                    $css = $cssResponse.Content

                    # Check for TOC-specific CSS
                    $hasTOCCSS = $css -match '\.toc-container|\.toc-sidebar|\.post-container'
                    Test-Result "TOC CSS Classes" $hasTOCCSS "TOC styling found"

                    # Check for responsive design
                    $hasResponsive = $css -match '@media.*max-width.*1024px'
                    Test-Result "Responsive CSS" $hasResponsive "Mobile breakpoints found"

                    # Check for CSS Grid
                    $hasGrid = $css -match 'display:\s*grid|grid-template-columns'
                    Test-Result "CSS Grid Layout" $hasGrid "Grid layout CSS found"

                    # Check for sticky positioning
                    $hasSticky = $css -match 'position:\s*sticky'
                    Test-Result "Sticky Positioning" $hasSticky "Sticky CSS found"
                }
            } catch {
                Test-Result "CSS Asset Loading" $false "Error loading CSS"
            }

            # Test 5: Performance check
            Write-Host "`n📋 Performance Tests" -ForegroundColor Cyan

            $responseTimes = @()
            for ($i = 1; $i -le 3; $i++) {
                try {
                    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
                    $response = Invoke-WebRequest -Uri "http://localhost:4000/2025/09/30/jekyll-blog-security-hardening-journey.html" -TimeoutSec 10
                    $stopwatch.Stop()

                    $responseTimes += $stopwatch.ElapsedMilliseconds
                    Test-Result "Performance Test $i" ($response.StatusCode -eq 200) "$($stopwatch.ElapsedMilliseconds)ms"
                } catch {
                    Test-Result "Performance Test $i" $false "Request failed"
                }
            }

            if ($responseTimes.Count -gt 0) {
                $avgTime = ($responseTimes | Measure-Object -Average).Average
                Test-Result "Average Response Time" ($avgTime -lt 2000) "$([math]::Round($avgTime, 0))ms average"
            }
        }
    }
} catch {
    Test-Result "Container Setup" $false "Error: $($_.Exception.Message)"
}

# Cleanup
Write-Host "`n🧹 Cleanup" -ForegroundColor Yellow
try {
    docker-compose down 2>$null | Out-Null
    Test-Result "Container Cleanup" $true "Containers stopped"
} catch {
    Test-Result "Container Cleanup" $false "Cleanup error"
}

# Results summary
Write-Host "`n📊 Test Summary" -ForegroundColor Green
Write-Host "===============" -ForegroundColor Green
$total = $passed + $failed
Write-Host "Total Tests: $total" -ForegroundColor White
Write-Host "✅ Passed: $passed" -ForegroundColor Green
Write-Host "❌ Failed: $failed" -ForegroundColor Red

if ($failed -eq 0) {
    Write-Host "`n🎉 All tests passed! TOC functionality verified." -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n💥 $failed test(s) failed. Review results above." -ForegroundColor Red
    exit 1
}