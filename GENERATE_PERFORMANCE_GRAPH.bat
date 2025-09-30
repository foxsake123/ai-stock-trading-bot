@echo off
REM Performance Graph Generation
REM Generates comparative performance visualization for DEE-BOT and SHORGAN-BOT

echo ============================================================
echo AI TRADING BOT - PERFORMANCE GRAPH GENERATOR
echo ============================================================
echo.

python generate_performance_graph.py

echo.
echo ============================================================
echo Graph saved to: performance_results.png
echo ============================================================
echo.

pause