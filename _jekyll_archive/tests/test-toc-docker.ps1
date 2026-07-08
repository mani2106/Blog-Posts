# TOC Docker Testing Script
Write-Host "TOC Functionality Docker Tests" -ForegroundColor Green

$passed = 0
$failed = 0

function Test-Result {
    param($name, $condition, $details = "")
    if ($condition) {
        Write-Host "PASS: $name" -ForegroundColor Green
        if ($details) { Write-Host "      $details" -ForegroundColor Gray }
        $script:passed++
    } else {
        Write-Host "FAIL: $name" -ForegroundColor Red
        if ($details) { Write-Host "      $details" -ForegroundColor Gray }
        $script:failed++
    }
}

# Test Docker availability
Write-Host "`nEnvironment Tests" -ForegroundColor Cyan
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

# Start Jekyll container
Write-Host "`nContainer Tests" -ForegroundColor Cyan
Write-Host "Starting Jekyll container..." -ForegroundColor Yellow

try {
    # Clean up existing containers
    docker-compose down 2>$null | Out-Null

    # Start Jekyll service
    $startResult = docker-compose up -d jekyll 2>&1
    Test-Result "Jekyll Container Start" ($LASTEXITCODE -eq 0) "Container started"

    if ($LASTEXITCODE -eq 0) {
        # Wait for Jekyll to be ready
        Write-Host "Waiting for Jekyll to be ready..." -ForegroundColor Yellow
        $ready = $false
        $attempts = 0
        $maxAttempts = 24

        while (-not $ready -and $attempts -lt $maxAttempts) {
            Start-Sleep -Seconds 5
            $attempts++

            try {
                $response = Invoke-WebRequest -Uri "http://localhost:4000/Blog-Posts/" -TimeoutSec 3 -ErrorAction SilentlyContinue
                if ($response.StatusCode -eq 200) {
                    $ready = $true
                }
            } catch {
                # Continue waiting
            }

            if ($attempts % 4 -eq 0) {
                Write-Host "Attempt $attempts of $maxAttempts..." -ForegroundColor Gray
            }
        }

        Test-Result "Jekyll Ready" $ready "Responded after $($attempts * 5) seconds"

        if ($ready) {
            # Test TOC functionality
            Write-Host "`nTOC Functionality Tests" -ForegroundColor Cyan

            # Test different posts with various TOC scenarios
            $testUrls = @(
                @{
                    Name = "Security Hardening Post"
                    Url = "http://localhost:4000/Blog-Posts/security/jekyll/ruby/devops/maintenance/kiro/spec-driven-development/2025/09/30/jekyll-blog-security-hardening-journey.html"
                    ExpectTOC = $true
                    Description = "Long post with many headers - should have TOC"
                },
                @{
                    Name = "Linear Regression Post"
                    Url = "http://localhost:4000/Blog-Posts/implementation/machine%20learning/linear%20regression/2020/08/31/linear-regression-grad-desc.html"
                    ExpectTOC = $true
                    Description = "Technical post with math - should have TOC"
                },
                @{
                    Name = "Probability Post"
                    Url = "http://localhost:4000/Blog-Posts/d2l.ai-exercises/deep-learning/tensorflow/2021/05/23/probability.html"
                    ExpectTOC = $true
                    Description = "Notebook-based post - should have TOC"
                },
                @{
                    Name = "Calculus Post"
                    Url = "http://localhost:4000/Blog-Posts/d2l.ai-exercises/deep-learning/tensorflow/2021/04/25/calculus_nb.html"
                    ExpectTOC = $true
                    Description = "Math-heavy post - should have TOC"
                },
                @{
                    Name = "Model Agnostic Post"
                    Url = "http://localhost:4000/Blog-Posts/take-home/implementation/2021/05/29/model-agnostic-featimp.html"
                    ExpectTOC = $false
                    Description = "Short post - may not have TOC (fewer than 2 headers)"
                }
            )

            foreach ($testCase in $testUrls) {
                $postName = $testCase.Name
                $url = $testCase.Url
                $expectTOC = $testCase.ExpectTOC

                try {
                    $response = Invoke-WebRequest -Uri $url -TimeoutSec 10 -ErrorAction SilentlyContinue

                    if ($response.StatusCode -eq 200) {
                        Test-Result "$postName - Page Load" $true "HTTP 200 OK"

                        $html = $response.Content

                        # Check for TOC container presence
                        $hasTOCContainer = $html -match 'class="toc-container"'
                        Test-Result "$postName - TOC Container Present" $hasTOCContainer "TOC container structure found"

                        # Check if TOC should be visible or hidden based on content
                        if ($expectTOC) {
                            # For posts that should have TOC, verify it's functional
                            $hasTOCContent = $html -match '<div id="toc".*?</div>' -and $html -match '<ul>'
                            Test-Result "$postName - TOC Content Generated" $hasTOCContent "TOC links generated"

                            # Check for proper header structure
                            $hasHeaders = $html -match '<h[2-6][^>]*id='
                            Test-Result "$postName - Headers with IDs" $hasHeaders "Headers have proper IDs for linking"
                        } else {
                            # For posts that shouldn't have TOC, verify it's hidden appropriately
                            $tocHidden = $html -match 'style="display:\s*none"' -or -not ($html -match '<ul>')
                            Test-Result "$postName - TOC Appropriately Hidden" $tocHidden "TOC hidden for short content"
                        }

                        # Check for ARIA attributes (should always be present)
                        $hasARIA = $html -match 'role="complementary"' -and $html -match 'aria-labelledby'
                        Test-Result "$postName - ARIA Attributes" $hasARIA "Accessibility attributes present"

                        # Check for TOC JavaScript (should always be loaded)
                        $hasJS = $html -match 'initializeTOC' -and $html -match 'validateTOCImplementation'
                        Test-Result "$postName - TOC JavaScript" $hasJS "TOC JavaScript and validation loaded"

                        # Check for performance optimizations
                        $hasOptimizations = $html -match 'throttle.*16' -and $html -match 'debounce'
                        Test-Result "$postName - Performance Optimizations" $hasOptimizations "60fps throttling and debouncing present"

                        # Check for cross-browser compatibility features
                        $hasPolyfills = $html -match 'Array\.from.*polyfill' -and $html -match 'NodeList.*forEach'
                        Test-Result "$postName - Cross-browser Polyfills" $hasPolyfills "IE11 compatibility polyfills present"

                        # Check for KaTeX math rendering (if post contains math)
                        $hasKaTeX = $html -match 'katex\.min\.css' -and $html -match 'katex\.min\.js'
                        $hasMathContent = $html -match '\$.*\$' -or $html -match '\\[.*\\]'
                        if ($hasMathContent) {
                            Test-Result "$postName - KaTeX Math Rendering" $hasKaTeX "KaTeX loaded for math content"

                            # Check for MathJax fallback
                            $hasMathJax = $html -match 'MathJax\.js'
                            Test-Result "$postName - MathJax Fallback" $hasMathJax "MathJax available as fallback"
                        } else {
                            Test-Result "$postName - Math Libraries Available" $hasKaTeX "Math rendering libraries loaded"
                        }

                        # Check for comments section (Utterances)
                        $hasComments = $html -match 'utteranc\.es/client\.js' -and $html -match 'repo="mani2106/Blog-Posts"'
                        Test-Result "$postName - Comments Integration" $hasComments "Utterances comments system loaded"

                        # Check for proper meta tags and SEO
                        $hasSEO = $html -match 'Jekyll SEO tag' -and $html -match 'og:title' -and $html -match 'twitter:card'
                        Test-Result "$postName - SEO Meta Tags" $hasSEO "SEO and social media tags present"

                        # Check for syntax highlighting
                        $hasSyntaxHighlight = $html -match 'highlight' -and $html -match 'language-'
                        Test-Result "$postName - Syntax Highlighting" $hasSyntaxHighlight "Code syntax highlighting available"

                    } else {
                        Test-Result "$postName - Page Load" $false "HTTP $($response.StatusCode)"
                    }
                } catch {
                    Test-Result "$postName - Page Load" $false "Error: $($_.Exception.Message)"
                }
            }

            # Test responsive design and accessibility
            Write-Host "`nResponsive Design Tests" -ForegroundColor Cyan

            try {
                # Test a post with User-Agent simulating mobile device
                $mobileHeaders = @{
                    'User-Agent' = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1'
                }

                $mobileResponse = Invoke-WebRequest -Uri "http://localhost:4000/Blog-Posts/security/jekyll/ruby/devops/maintenance/kiro/spec-driven-development/2025/09/30/jekyll-blog-security-hardening-journey.html" -Headers $mobileHeaders -TimeoutSec 10

                if ($mobileResponse.StatusCode -eq 200) {
                    $mobileHtml = $mobileResponse.Content

                    # Check for responsive viewport meta tag
                    $hasViewport = $mobileHtml -match 'viewport.*width=device-width'
                    Test-Result "Mobile - Viewport Meta Tag" $hasViewport "Responsive viewport configuration present"

                    # Check for mobile-specific CSS
                    $hasMobileCSS = $mobileHtml -match '@media.*max-width.*1024px'
                    Test-Result "Mobile - Responsive CSS" $hasMobileCSS "Mobile breakpoints in CSS"

                    # TOC should still be present but hidden on mobile
                    $hasTOCStructure = $mobileHtml -match 'toc-sidebar'
                    Test-Result "Mobile - TOC Structure Present" $hasTOCStructure "TOC structure available for progressive enhancement"
                }
            } catch {
                Test-Result "Mobile Responsive Tests" $false "Error testing mobile responsiveness"
            }

            # Test CSS loading
            Write-Host "`nCSS and Asset Tests" -ForegroundColor Cyan

            try {
                $cssResponse = Invoke-WebRequest -Uri "http://localhost:4000/Blog-Posts/assets/css/style.css" -TimeoutSec 10
                Test-Result "CSS Asset Loading" ($cssResponse.StatusCode -eq 200) "Main stylesheet loaded"

                if ($cssResponse.StatusCode -eq 200) {
                    $css = $cssResponse.Content

                    # Check for TOC-specific CSS
                    $hasTOCCSS = $css -match '\.toc-container'
                    Test-Result "TOC CSS Classes" $hasTOCCSS "TOC styling found"

                    # Check for responsive design
                    $hasResponsive = $css -match '@media.*max-width'
                    Test-Result "Responsive CSS" $hasResponsive "Mobile breakpoints found"

                    # Check for CSS Grid
                    $hasGrid = $css -match 'grid-template-columns'
                    Test-Result "CSS Grid Layout" $hasGrid "Grid layout CSS found"

                    # Check for sticky positioning
                    $hasSticky = $css -match 'position:\s*sticky'
                    Test-Result "Sticky Positioning" $hasSticky "Sticky CSS found"

                    # Check for performance optimizations in CSS
                    $hasHardwareAccel = $css -match 'transform:\s*translateZ\(0\)' -and $css -match 'will-change'
                    Test-Result "CSS Performance Optimizations" $hasHardwareAccel "Hardware acceleration and will-change properties"

                    # Check for accessibility features in CSS
                    $hasA11yCSS = $css -match 'prefers-reduced-motion' -and $css -match 'prefers-contrast'
                    Test-Result "CSS Accessibility Features" $hasA11yCSS "Reduced motion and high contrast support"
                }
            } catch {
                Test-Result "CSS Asset Loading" $false "Error loading CSS"
            }

            # Test RSS Feed generation
            Write-Host "`nFeed and SEO Tests" -ForegroundColor Cyan

            try {
                $feedResponse = Invoke-WebRequest -Uri "http://localhost:4000/Blog-Posts/feed.xml" -TimeoutSec 10
                Test-Result "RSS Feed Generation" ($feedResponse.StatusCode -eq 200) "RSS feed accessible"

                if ($feedResponse.StatusCode -eq 200) {
                    $feedContent = $feedResponse.Content

                    # Check for valid RSS structure
                    $hasValidRSS = $feedContent -match '<rss.*version="2.0"' -and $feedContent -match '<channel>'
                    Test-Result "RSS Feed Structure" $hasValidRSS "Valid RSS 2.0 structure"

                    # Check for recent posts in feed
                    $hasRecentPosts = $feedContent -match 'jekyll-blog-security-hardening-journey'
                    Test-Result "RSS Feed Content" $hasRecentPosts "Recent posts included in feed"
                }
            } catch {
                Test-Result "RSS Feed Tests" $false "Error testing RSS feed"
            }

            # Test sitemap generation
            try {
                $sitemapResponse = Invoke-WebRequest -Uri "http://localhost:4000/Blog-Posts/sitemap.xml" -TimeoutSec 10
                Test-Result "Sitemap Generation" ($sitemapResponse.StatusCode -eq 200) "XML sitemap accessible"

                if ($sitemapResponse.StatusCode -eq 200) {
                    $sitemapContent = $sitemapResponse.Content

                    # Check for valid sitemap structure
                    $hasValidSitemap = $sitemapContent -match '<urlset.*xmlns' -and $sitemapContent -match '<url>'
                    Test-Result "Sitemap Structure" $hasValidSitemap "Valid XML sitemap structure"
                }
            } catch {
                Test-Result "Sitemap Tests" $false "Error testing sitemap"
            }

            # Test specific functionality scenarios
            Write-Host "`nSpecific Functionality Tests" -ForegroundColor Cyan

            # Test a math-heavy post specifically for KaTeX
            try {
                $mathPostUrl = "http://localhost:4000/Blog-Posts/d2l.ai-exercises/deep-learning/tensorflow/2021/05/23/probability.html"
                $mathResponse = Invoke-WebRequest -Uri $mathPostUrl -TimeoutSec 10

                if ($mathResponse.StatusCode -eq 200) {
                    $mathHtml = $mathResponse.Content

                    # Check for actual math equations in the content
                    $hasMathEquations = $mathHtml -match '\$\$.*\$\$' -or $mathHtml -match '\$[^$]+\$'
                    Test-Result "Math Post - Equations Present" $hasMathEquations "LaTeX math equations found in content"

                    # Check for KaTeX rendering setup
                    $hasKaTeXSetup = $mathHtml -match 'renderMathInElement' -and $mathHtml -match 'delimiters'
                    Test-Result "Math Post - KaTeX Configuration" $hasKaTeXSetup "KaTeX auto-render configured"

                    # Check for math-specific CSS
                    $hasMathCSS = $mathHtml -match 'katex\.min\.css'
                    Test-Result "Math Post - Math Styling" $hasMathCSS "KaTeX CSS loaded for proper math display"
                }
            } catch {
                Test-Result "Math Post Tests" $false "Error testing math functionality"
            }

            # Test notebook-based post for special formatting
            try {
                $notebookUrl = "http://localhost:4000/Blog-Posts/d2l.ai-exercises/deep-learning/tensorflow/2021/04/25/calculus_nb.html"
                $notebookResponse = Invoke-WebRequest -Uri $notebookUrl -TimeoutSec 10

                if ($notebookResponse.StatusCode -eq 200) {
                    $notebookHtml = $notebookResponse.Content

                    # Check for notebook-specific elements
                    $hasNotebookElements = $notebookHtml -match 'cell.*border-box-sizing' -or $notebookHtml -match 'inner_cell'
                    Test-Result "Notebook Post - Jupyter Elements" $hasNotebookElements "Jupyter notebook formatting preserved"

                    # Check for code cells with syntax highlighting
                    $hasCodeCells = $notebookHtml -match 'highlight.*python' -or $notebookHtml -match 'language-python'
                    Test-Result "Notebook Post - Code Highlighting" $hasCodeCells "Python code syntax highlighting working"
                }
            } catch {
                Test-Result "Notebook Post Tests" $false "Error testing notebook functionality"
            }

            # Test home page (should not have TOC)
            Write-Host "`nHome Page Tests" -ForegroundColor Cyan

            try {
                $homeResponse = Invoke-WebRequest -Uri "http://localhost:4000/Blog-Posts/" -TimeoutSec 10
                Test-Result "Home Page Load" ($homeResponse.StatusCode -eq 200) "Blog index accessible"

                if ($homeResponse.StatusCode -eq 200) {
                    $homeHtml = $homeResponse.Content

                    # Home page should not have active TOC content
                    $noActiveTOC = -not ($homeHtml -match '<div id="toc">.*<ul>')
                    Test-Result "Home Page - No Active TOC" $noActiveTOC "TOC not active on index page"

                    # But TOC JavaScript should still be loaded for potential future use
                    $hasJS = $homeHtml -match 'initializeTOC'
                    Test-Result "Home Page - TOC JS Available" $hasJS "TOC JavaScript loaded for consistency"
                }
            } catch {
                Test-Result "Home Page Load" $false "Error loading home page"
            }

            # Performance test
            Write-Host "`nPerformance Tests" -ForegroundColor Cyan

            # Test performance across different post types
            $performanceUrls = @(
                "http://localhost:4000/Blog-Posts/security/jekyll/ruby/devops/maintenance/kiro/spec-driven-development/2025/09/30/jekyll-blog-security-hardening-journey.html",
                "http://localhost:4000/Blog-Posts/d2l.ai-exercises/deep-learning/tensorflow/2021/05/23/probability.html",
                "http://localhost:4000/Blog-Posts/implementation/machine%20learning/linear%20regression/2020/08/31/linear-regression-grad-desc.html"
            )

            $responseTimes = @()
            $testCount = 0

            foreach ($perfUrl in $performanceUrls) {
                $testCount++
                $postType = if ($perfUrl -match "security") { "Long Post" }
                           elseif ($perfUrl -match "probability") { "Notebook Post" }
                           else { "Technical Post" }

                try {
                    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
                    $response = Invoke-WebRequest -Uri $perfUrl -TimeoutSec 10
                    $stopwatch.Stop()

                    $responseTimes += $stopwatch.ElapsedMilliseconds
                    Test-Result "Performance Test $testCount ($postType)" ($response.StatusCode -eq 200) "$($stopwatch.ElapsedMilliseconds)ms"
                } catch {
                    Test-Result "Performance Test $testCount ($postType)" $false "Request failed"
                }
            }

            if ($responseTimes.Count -gt 0) {
                $avgTime = ($responseTimes | Measure-Object -Average).Average
                Test-Result "Average Response Time" ($avgTime -lt 2000) "$([math]::Round($avgTime, 0))ms average"
            }
        }
    }
} catch {
    Test-Result "Container Setup" $false "Setup error"
}

# Cleanup
Write-Host "`nCleanup" -ForegroundColor Yellow
try {
    docker-compose down 2>$null | Out-Null
    Test-Result "Container Cleanup" $true "Containers stopped"
} catch {
    Test-Result "Container Cleanup" $false "Cleanup error"
}

# Results summary
Write-Host "`nTest Summary" -ForegroundColor Green
Write-Host "============" -ForegroundColor Green
$total = $passed + $failed
Write-Host "Total Tests: $total" -ForegroundColor White
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red

if ($failed -eq 0) {
    Write-Host "`nAll tests passed! TOC functionality verified." -ForegroundColor Green
    exit 0
} else {
    Write-Host "`nSome tests failed. Review results above." -ForegroundColor Red
    exit 1
}