# Portfolio Analytics Dashboard v1.0

[cite_start]An interactive, high-performance quantitative finance dashboard built with Streamlit, Pandas, and Plotly[cite: 211, 212]. [cite_start]This application empowers investors to construct portfolios, simulate asset allocations via Modern Portfolio Theory (MPT), and execute deep-dive risk and performance benchmarking against major market indices[cite: 213].

## Key Features

* [cite_start]**Global Asset Engine:** Integrated Live API search tool parsing equities and ETFs directly via Yahoo Finance[cite: 215].
* [cite_start]**Monte Carlo Optimization:** Executes up to 100,000 parallel portfolio simulations to map out the Efficient Frontier and isolate the Maximum Sharpe Ratio configuration[cite: 217].
* [cite_start]**Adaptive Portfolio Allocation:** Dynamic asset rebalancing chart containing an automatic micro-position aggregation threshold (positions merge into an "Others" category to preserve visualization neatness)[cite: 218].
* [cite_start]**Historical Benchmarking:** Side-by-side performance comparison against benchmark assets (SPY, QQQ, URTH) mapping cumulative returns[cite: 219, 220, 221, 222].
* [cite_start]**Advanced Risk Diagnostics:** * Real-time multi-asset correlation matrices[cite: 222].
  * [cite_start]Historical peak-to-trough Drawdown Analysis tracking maximum structural losses[cite: 225].
  * [cite_start]Time-varying Rolling Sharpe Ratio curves (252-day window) evaluating active risk-adjusted consistency[cite: 226].

## Tech Stack

* [cite_start]**UI Framework:** Streamlit (Custom Darkmode injection via CSS overrides) [cite: 228]
* [cite_start]**Data Pipelines:** yfinance API, Requests [cite: 229]
* [cite_start]**Vectorized Math Engine:** NumPy, Pandas [cite: 231]
* [cite_start]**Visualization Layer:** Plotly Express (Fully reactive, customized SVG/HTML graphing) [cite: 232]

---

## 1. Mathematical Architecture

[cite_start]The core framework underlying this analytical application relies on mathematical formulations derived from Modern Portfolio Theory (MPT) introduced by Harry Markowitz, alongside modern risk management metrics[cite: 234].

### Multi-Asset Return and Covariance Engine
[cite_start]Daily asset returns are transformed into vectorized annualized parameters assuming 252 trading days per calendar year[cite: 236]. [cite_start]Let $\mu$ be the daily return vector and $\Sigma$ be the daily covariance matrix of returns[cite: 237]. [cite_start]The annualized expected return vector $R_{a}$ and covariance matrix $\Sigma_{a}$ are[cite: 238]:

$$R_{a} = \mu \times 252$$
$$\Sigma_{a} = \Sigma \times 252$$

### Monte Carlo Simulation & Optimization
[cite_start]The system generates random weight vectors $\omega = [\omega_{1}, \omega_{2}, ..., \omega_{n}]^{T}$[cite: 241]. [cite_start]For each simulation pass, weights are strictly normalized to fulfill the long-only budget constraint[cite: 241]:

$$\sum_{i=1}^{n} \omega_{i} = 1 \quad \text{where} \quad \omega_{i} \ge 0$$

[cite_start]For each generated weight vector, the expected portfolio return $R_{p}$ and the overall portfolio volatility $\sigma_{p}$ are computed using linear algebra matrix operations[cite: 243]:

$$R_{p} = \omega^{T} R_{a}$$
$$\sigma_{p} = \sqrt{\omega^{T} \Sigma_{a} \omega}$$

### Risk-adjusted Performance (Sharpe Ratio)
[cite_start]Assuming a risk-free rate of $R_{f} = 0$ (version 1.0), the maximum risk-adjusted performance optimization target is determined via[cite: 246]:

$$\text{Sharpe Ratio} = \frac{R_{p} - R_{f}}{\sigma_{p}}$$

### Continuous Risk Diagnostics
[cite_start]The Max Drawdown (DD) monitors structural asset capital declines[cite: 249]. [cite_start]Let $Y_{t}$ be the portfolio's cumulated value at time $t$[cite: 249]. [cite_start]The drawdown trajectory is defined as[cite: 250]:

$$DD_{t} = \frac{Y_{t} - \max_{\tau \le t}(Y_{\tau})}{\max_{\tau \le t}(Y_{\tau})}$$

[cite_start]Similarly to the Sharpe Ratio, the Rolling Sharpe Ratio is formed by dividing the difference of the arithmetic mean of the daily returns and the risk-free rate with the standard deviation of the daily returns[cite: 252]. [cite_start]Note that instead of using a yearly average, the annualized rolling return and volatility are calculated dynamically[cite: 253].

---

## 2. Portfolio Analysis

[cite_start]In the following, a portfolio containing the shares of listed companies will be analyzed[cite: 255]:
* [cite_start]Alphabet Inc. [cite: 258]
* [cite_start]Amazon.com [cite: 259]
* [cite_start]Berkshire Hathaway (B) [cite: 260]
* [cite_start]Coca-Cola Company [cite: 261]
* [cite_start]GameStop Corporation [cite: 262]
* [cite_start]Meta Platforms [cite: 263]
* [cite_start]Microsoft Corporation [cite: 264]
* [cite_start]NVIDIA Corporation [cite: 265]
* [cite_start]Procter & Gamble [cite: 267]
* [cite_start]SAP [cite: 268]

[cite_start]The Monte Carlo Simulation (10,000 random simulations; Jan. 1, 2020 – Feb. 6, 2026) indicates a rather high maximum Sharpe Ratio as well as a high annual return[cite: 269]. [cite_start]However, this comes at the cost of higher volatility and a moderate drawdown[cite: 270].

![KPI Overview](Images/3/KPI-Cards.png)

### Asset Allocation & Structure
[cite_start]It implies an allocation mostly combining constantly well-performing and diversified companies, such as Berkshire Hathaway, Coca-Cola and Procter & Gamble, as well as recently out-performing shares of tech-giants like NVIDIA and Alphabet[cite: 286]. [cite_start]With a share of almost 10%, GameStop's hyped share contributes a significant amount to the portfolio[cite: 287]. [cite_start]Because Meta Platforms, Microsoft Corporation and SAP would only make up $\le 2\%$ of the allocation, they are listed in the category "Others"[cite: 288].

![Portfolio Allocation](Images/4/Optimization_Portfolio Allocation.png) 
![Portfolio Allocation](Images/4.1/Optimization_Portfolio Allocation Table.png)
*Figure 1: Maximum Sharpe Portfolio Allocation. [cite_start]Visual breakdown and tabulated shares of the optimized asset weights[cite: 308]. [cite_start]Minor positions ($\le 2\%$) are dynamically aggregated into the "Others" category to ensure structural clarity[cite: 309].*

### 2.1. Historical Performance and Benchmarking
[cite_start]To evaluate the historical efficacy of the Maximum Sharpe Portfolio, a retrospective performance analysis was conducted for the period from January 1, 2020, to February 6, 2026[cite: 312]. [cite_start]The optimized portfolio's cumulative returns are benchmarked against the broad market index (MSCI World) to measure structural outperformance and tracking behavior under various market regimes[cite: 312].

[cite_start]As visualized below, the strategic allocation successfully captured strong secular tailwinds, primarily driven by the significant alpha generated by mega-cap technology exposure and the tactical inclusion of high-momentum assets[cite: 313]. [cite_start]Throughout the observed timeline, the optimized portfolio demonstrates a persistent trajectory of outperformance relative to the benchmark, validating the risk-adjusted scaling achieved through the Monte Carlo simulation[cite: 314].

![Cumulative Returns](Images/5/Performance_Cumulative Returns.png)
*Figure 2: Cumulative Returns vs. Benchmark. [cite_start]Comparative growth path of the optimized Maximum Sharpe Portfolio (blue) against the selected market benchmark (red) from 2020 to 2026[cite: 330]. [cite_start]Returns are plotted as percentage growth, demonstrating a substantial performance spread over the long term[cite: 330].*

### 3.2 Consistency of Risk-Adjusted Returns (Rolling Sharpe Ratio)
[cite_start]While cumulative returns illustrate absolute growth, they do not reflect whether the performance was achieved through structural efficiency or highly volatile, short-term surges[cite: 332]. [cite_start]To analyze the temporal consistency of the portfolio's risk-adjusted outperformance, a 252-day moving window was utilized to calculate the rolling Sharpe Ratio[cite: 333].

[cite_start]The rolling analysis reveals that the optimized portfolio maintained a superior risk-adjusted profile compared to the benchmark across the majority of the observed market regimes[cite: 334]. [cite_start]Even during macroeconomic shifts and periods of heightened market compression, the portfolio's rolling metric consistently rebounded faster and remained predominantly above the zero-line[cite: 335]. [cite_start]This cyclical persistence proves that the allocation model successfully maximized diversified returns per unit of portfolio volatility, rather than just taking on uncompensated beta[cite: 336, 338].

![Rolling Sharpe Ratio](Images/5.1/Performance_Rolling Sharpe Ratio.png)
*Figure 3: 252-Day Rolling Sharpe Ratio. Time-varying risk-adjusted performance of the optimized portfolio (blue) versus the benchmark index (red)[cite: 355]. The dashed gray line indicates a Sharpe Ratio of zero, serving as the threshold for positive risk-adjusted excess returns[cite: 356].*

### 3.3 Risk Diagnostics and Structural Vulnerability
[cite_start]To achieve a comprehensive understanding of the portfolio's risk profile, the final dimension of the analysis focuses on structural downside vulnerability and underlying asset dependencies[cite: 359].

[cite_start]The Drawdown Analysis evaluates the historical peak-to-trough declines, charting the continuous "underwater" periods of both the portfolio and the benchmark[cite: 360]. [cite_start]While the optimized portfolio generated significant alpha, it also experienced a maximum drawdown of -34.9%, driven by the high-beta technology exposure and momentum stocks like GameStop[cite: 361]. [cite_start]However, the recovery timeline aligns closely with the broader market, indicating that the portfolio's drawdowns were cyclical rather than structural collapses[cite: 362].

[cite_start]The major difference does not lie in the drawdown's strength but in the occurring date[cite: 363]. [cite_start]In comparison to the benchmark, which experienced a similar drawdown of -34.0% in 2020, the portfolio's maximum drawdown happened in 2022, caused by the weakening of tech-stocks because of rapidly increasing interest rates and the fall of meme-stocks like GameStop[cite: 364].

![Historical Drawdown](Images/6/Risk_Drawdown Analysis.png)
*Figure 4: Historical Drawdown Analysis. Visual representation of peak-to-trough capital declines for the optimized portfolio (blue) and the benchmark (red)[cite: 378]. Shaded areas illustrate the depth and duration of recovery periods from all-time highs[cite: 379].*

[cite_start]The structural resilience behind these metrics is explained by the Correlation Matrix[cite: 380]. [cite_start]By balancing hyper-growth tech giants (e.g., NVIDIA, Alphabet) with low-correlation, defensive staples (e.g., Coca-Cola, Procter & Gamble, Berkshire Hathaway), the allocation mechanism effectively exploited diversification benefits[cite: 381]. [cite_start]The statistical decoupling between these asset classes successfully mitigated systemic tail risk, ensuring that idiosyncratic shocks from individual speculative holdings did not destabilize the aggregate portfolio architecture[cite: 382].

![Correlation Matrix](Images/6.1/Risk_Correlation Matrix.png)
[cite_start]*Figure 5: Statistical matrix mapping the Pearson correlation coefficients among the selected portfolio constituents[cite: 404]. The color spectrum from blue (positive correlation) to red (negative correlation) illustrates the structural diversification potential within the basket[cite: 405].*

---

## 3. How to run it

[cite_start]To run this analytics dashboard on your local machine, follow these three simple steps[cite: 409]:

### 1. Clone the Repository & Navigate
[cite_start]Open your terminal/command prompt and clone this repository, then switch into the project directory[cite: 411]:
```bash
git clone [https://github.com/JuSt2711/Portfolio-Analytics-Dashboard.git](https://github.com/JuSt2711/Portfolio-Analytics-Dashboard.git)
cd Portfolio-Analytics-Dashboard

### 2. Install dependencies
Install all required libraries using pip
pip install streamlit numpy pandas yfinance plotly requests

### 3. Launch dashboard
Start the local Streamlit server
streamlit run app.py
