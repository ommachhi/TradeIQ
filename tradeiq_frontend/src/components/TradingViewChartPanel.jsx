import { memo, useEffect, useMemo, useRef, useState } from 'react'
import html2canvas from 'html2canvas'
import {
  createChart,
  ColorType,
  CrosshairMode,
  LineStyle,
  CandlestickSeries,
  LineSeries,
  HistogramSeries,
} from 'lightweight-charts'

const TIMEFRAMES = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '5y']

const addSeriesCompat = (chart, type, options) => {
  if (type === 'candlestick') {
    if (typeof chart.addCandlestickSeries === 'function') {
      return chart.addCandlestickSeries(options)
    }
    return chart.addSeries(CandlestickSeries, options)
  }
  if (type === 'line') {
    if (typeof chart.addLineSeries === 'function') {
      return chart.addLineSeries(options)
    }
    return chart.addSeries(LineSeries, options)
  }
  if (type === 'histogram') {
    if (typeof chart.addHistogramSeries === 'function') {
      return chart.addHistogramSeries(options)
    }
    return chart.addSeries(HistogramSeries, options)
  }
  throw new Error(`Unsupported chart series type: ${type}`)
}

const addDays = (timeValue, days) => {
  const base = new Date(timeValue)
  if (Number.isNaN(base.getTime())) {
    return null
  }
  base.setDate(base.getDate() + days)
  return base.toISOString().slice(0, 10)
}

const toChartRows = (rows) => {
  if (!Array.isArray(rows)) {
    return []
  }

  return rows
    .map((row) => ({
      time: row.time || row.date || row.Date,
      open: Number(row.open ?? row.Open ?? 0),
      high: Number(row.high ?? row.High ?? 0),
      low: Number(row.low ?? row.Low ?? 0),
      close: Number(row.close ?? row.Close ?? 0),
      volume: Number(row.volume ?? row.Volume ?? 0),
    }))
    .filter((row) => row.time && Number.isFinite(row.open) && Number.isFinite(row.high) && Number.isFinite(row.low) && Number.isFinite(row.close))
    .sort((a, b) => String(a.time).localeCompare(String(b.time)))
}

const rollingAverage = (rows, length, key) => {
  const result = []
  let sum = 0
  for (let i = 0; i < rows.length; i += 1) {
    sum += rows[i][key]
    if (i >= length) {
      sum -= rows[i - length][key]
    }
    if (i >= length - 1) {
      result.push({ time: rows[i].time, value: sum / length })
    }
  }
  return result
}

const buildRSI = (rows, period = 14) => {
  if (rows.length < period + 1) {
    return []
  }

  const changes = []
  for (let i = 1; i < rows.length; i += 1) {
    changes.push(rows[i].close - rows[i - 1].close)
  }

  let avgGain = 0
  let avgLoss = 0
  for (let i = 0; i < period; i += 1) {
    const value = changes[i]
    if (value >= 0) {
      avgGain += value
    } else {
      avgLoss += Math.abs(value)
    }
  }

  avgGain /= period
  avgLoss /= period

  const rsi = []
  const firstRs = avgLoss === 0 ? 100 : avgGain / avgLoss
  rsi.push({ time: rows[period].time, value: 100 - 100 / (1 + firstRs) })

  for (let i = period; i < changes.length; i += 1) {
    const value = changes[i]
    const gain = value > 0 ? value : 0
    const loss = value < 0 ? Math.abs(value) : 0

    avgGain = (avgGain * (period - 1) + gain) / period
    avgLoss = (avgLoss * (period - 1) + loss) / period

    const rs = avgLoss === 0 ? 100 : avgGain / avgLoss
    rsi.push({ time: rows[i + 1].time, value: 100 - 100 / (1 + rs) })
  }

  return rsi
}

const TradingViewChartPanel = ({
  symbol,
  data,
  prediction,
  timeframe,
  onTimeframeChange,
}) => {
  const wrapperRef = useRef(null)
  const chartRef = useRef(null)
  const tooltipRef = useRef(null)
  const apiRef = useRef({ reset: () => {}, fit: () => {} })

  const [chartType, setChartType] = useState('candlestick')
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [chartError, setChartError] = useState('')

  const rows = useMemo(() => toChartRows(data), [data])

  useEffect(() => {
    if (!wrapperRef.current || !chartRef.current || !rows.length) {
      setChartError('')
      return undefined
    }

    let chart = null
    let resizeObserver = null

    try {
      const width = wrapperRef.current.clientWidth
      const chartHeight = 580

    const baseLayout = {
      background: { type: ColorType.Solid, color: '#0b1220' },
      textColor: '#a7b4c6',
    }

    const grid = {
      vertLines: { color: '#172133' },
      horzLines: { color: '#172133' },
    }

    const crosshair = {
      mode: CrosshairMode.Normal,
      vertLine: { labelBackgroundColor: '#1f2a3d', color: '#334155', width: 1 },
      horzLine: { labelBackgroundColor: '#1f2a3d', color: '#334155', width: 1 },
    }

      chart = createChart(chartRef.current, {
      width,
        height: chartHeight,
      layout: baseLayout,
      grid,
      crosshair,
      handleScale: { mouseWheel: true, pinch: true, axisPressedMouseMove: true },
      handleScroll: { mouseWheel: true, pressedMouseMove: true, horzTouchDrag: true, vertTouchDrag: false },
      rightPriceScale: { borderColor: '#243145' },
      timeScale: { borderColor: '#243145', rightOffset: 12, fixLeftEdge: true },
    })

      const candlestickSeries = addSeriesCompat(chart, 'candlestick', {
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
      visible: chartType === 'candlestick',
    })

      const lineSeries = addSeriesCompat(chart, 'line', {
      color: '#60a5fa',
      lineWidth: 2,
      visible: chartType === 'line',
      crosshairMarkerVisible: true,
    })

      const ma50Series = addSeriesCompat(chart, 'line', { color: '#f59e0b', lineWidth: 2, title: 'MA50' })
      const ma200Series = addSeriesCompat(chart, 'line', { color: '#10b981', lineWidth: 2, title: 'MA200' })

      const forecast7Series = addSeriesCompat(chart, 'line', {
      color: '#a855f7',
      lineWidth: 2,
      lineStyle: LineStyle.Dashed,
      title: '7D Forecast',
    })

      const forecast30Series = addSeriesCompat(chart, 'line', {
      color: '#f97316',
      lineWidth: 2,
      lineStyle: LineStyle.Dotted,
      title: '30D Forecast',
    })

      const volumeSeries = addSeriesCompat(chart, 'histogram', {
      color: '#334155',
      priceFormat: { type: 'volume' },
        priceScaleId: 'volume-scale',
      })

      const volumeMASeries = addSeriesCompat(chart, 'line', {
        color: '#38bdf8',
        lineWidth: 1.5,
        title: 'Vol MA20',
        priceScaleId: 'volume-scale',
      })

      const rsiSeries = addSeriesCompat(chart, 'line', {
        color: '#facc15',
        lineWidth: 1,
        title: 'RSI(14)',
        priceScaleId: 'rsi-scale',
      })
      const rsiTopSeries = addSeriesCompat(chart, 'line', { color: '#64748b', lineStyle: LineStyle.Dotted, lineWidth: 1, priceScaleId: 'rsi-scale' })
      const rsiBottomSeries = addSeriesCompat(chart, 'line', { color: '#64748b', lineStyle: LineStyle.Dotted, lineWidth: 1, priceScaleId: 'rsi-scale' })

      chart.priceScale('volume-scale').applyOptions({
        scaleMargins: { top: 0.72, bottom: 0.16 },
        borderColor: '#243145',
      })
      chart.priceScale('rsi-scale').applyOptions({
        scaleMargins: { top: 0.84, bottom: 0.02 },
        borderColor: '#243145',
      })
      chart.priceScale('right').applyOptions({
        scaleMargins: { top: 0.04, bottom: 0.34 },
      })

      candlestickSeries.setData(rows)
      lineSeries.setData(rows.map((row) => ({ time: row.time, value: row.close })))

      const ma50 = rollingAverage(rows, 50, 'close')
      const ma200 = rollingAverage(rows, 200, 'close')
      const volumeMA = rollingAverage(rows, 20, 'volume')
      const rsi = buildRSI(rows)

      ma50Series.setData(ma50)
      ma200Series.setData(ma200)

      const volumeData = rows.map((row) => ({
      time: row.time,
      value: row.volume,
      color: row.close >= row.open ? 'rgba(34,197,94,0.8)' : 'rgba(239,68,68,0.8)',
    }))

      volumeSeries.setData(volumeData)
      volumeMASeries.setData(volumeMA)
      rsiSeries.setData(rsi)
      rsiTopSeries.setData(rows.map((row) => ({ time: row.time, value: 70 })))
      rsiBottomSeries.setData(rows.map((row) => ({ time: row.time, value: 30 })))

      if (prediction?.predicted_price) {
      const latestTime = rows[rows.length - 1]?.time
      const latestClose = rows[rows.length - 1]?.close
      const nextDay = prediction.predicted_price
      const forecast7 = prediction.forecast_7d ?? nextDay
      const forecast30 = prediction.forecast_30d ?? nextDay
      const day1Time = addDays(latestTime, 1)
      const day7Time = addDays(latestTime, 7)
      const day30Time = addDays(latestTime, 30)

      if (day7Time) {
        forecast7Series.setData([
          { time: latestTime, value: latestClose },
          { time: day7Time, value: forecast7 },
        ])
      }

      if (day30Time) {
        forecast30Series.setData([
          { time: latestTime, value: latestClose },
          { time: day30Time, value: forecast30 },
        ])
      }

      if (day1Time) {
        lineSeries.setData([
          ...rows.map((row) => ({ time: row.time, value: row.close })),
          { time: day1Time, value: nextDay },
        ])
      }
    }

      const formatVolume = (value) => {
      if (!value) return '0'
      if (value >= 1000000) return `${(value / 1000000).toFixed(2)}M`
      if (value >= 1000) return `${(value / 1000).toFixed(2)}K`
      return value.toFixed(0)
    }

      const tooltip = tooltipRef.current
      const onCrosshairMove = (param) => {
      if (!tooltip) {
        return
      }
      if (!param.time || !param.point || !param.seriesData) {
        tooltip.style.display = 'none'
        return
      }

      const candle = param.seriesData.get(candlestickSeries)
      const linePoint = param.seriesData.get(lineSeries)
      const point = candle || linePoint

      if (!point) {
        tooltip.style.display = 'none'
        return
      }

      const volume = param.seriesData.get(volumeSeries)
      tooltip.style.display = 'block'
      tooltip.style.left = `${Math.max(10, param.point.x + 16)}px`
      tooltip.style.top = `${Math.max(10, param.point.y + 16)}px`
      tooltip.innerHTML = `
        <div class="trading-tooltip-title">${symbol || 'SYMBOL'} ${String(param.time)}</div>
        <div>O ${Number(candle?.open ?? point.value ?? 0).toFixed(2)}</div>
        <div>H ${Number(candle?.high ?? point.value ?? 0).toFixed(2)}</div>
        <div>L ${Number(candle?.low ?? point.value ?? 0).toFixed(2)}</div>
        <div>C ${Number(candle?.close ?? point.value ?? 0).toFixed(2)}</div>
        <div>Vol ${formatVolume(Number(volume?.value || 0))}</div>
      `
    }

      chart.subscribeCrosshairMove(onCrosshairMove)

      resizeObserver = new ResizeObserver((entries) => {
      const nextWidth = entries[0].contentRect.width
        chart.applyOptions({ width: nextWidth })
    })

      resizeObserver.observe(wrapperRef.current)
      chart.timeScale().fitContent()

      apiRef.current = {
        reset: () => chart.timeScale().resetTimeScale(),
        fit: () => chart.timeScale().fitContent(),
      }
      setChartError('')
    } catch (error) {
      console.error('Trading chart initialization failed:', error)
      setChartError(error?.message || 'Chart failed to render. Please refresh the page.')
    }

    return () => {
      if (resizeObserver) {
        resizeObserver.disconnect()
      }
      if (chart) {
        chart.remove()
      }
    }
  }, [rows, chartType, prediction, symbol])

  const handleReset = () => {
    apiRef.current.reset()
  }

  const handleFit = () => {
    apiRef.current.fit()
  }

  const handleFullscreen = async () => {
    if (!wrapperRef.current) {
      return
    }

    if (!document.fullscreenElement) {
      await wrapperRef.current.requestFullscreen()
      setIsFullscreen(true)
    } else {
      await document.exitFullscreen()
      setIsFullscreen(false)
    }
  }

  const handleExport = async () => {
    if (!wrapperRef.current) {
      return
    }

    const canvas = await html2canvas(wrapperRef.current, {
      backgroundColor: '#0b1220',
      scale: 2,
    })

    const link = document.createElement('a')
    link.download = `${symbol || 'chart'}-${Date.now()}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
  }

  if (!rows.length) {
    return (
      <div className="card p-6">
        <h3 className="text-lg font-semibold mb-3">Trading Chart</h3>
        <p className="text-sm text-gray-300">No data available</p>
      </div>
    )
  }

  if (chartError) {
    return (
      <div className="card p-6">
        <h3 className="text-lg font-semibold mb-3">Trading Chart</h3>
        <p className="text-sm text-red-300">{chartError}</p>
      </div>
    )
  }

  return (
    <div className={`trading-panel card p-4 md:p-5 ${isFullscreen ? 'fullscreen-active' : ''}`}>
      <div className="trading-panel-top">
        <div>
          <h3 className="text-lg font-semibold text-white">{symbol || 'SYMBOL'} Trading Terminal</h3>
          <p className="text-xs text-slate-400">Candlestick + Volume + RSI</p>
        </div>

        <div className="trading-actions">
          <button type="button" onClick={handleReset}>Reset Zoom</button>
          <button type="button" onClick={handleFit}>Auto Fit</button>
          <button type="button" onClick={handleExport}>Export PNG</button>
          <button type="button" onClick={handleFullscreen}>{isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}</button>
        </div>
      </div>

      <div className="trading-row mt-4">
        <div className="selector-group">
          <span className="selector-label">Timeframe</span>
          {TIMEFRAMES.map((item) => (
            <button
              type="button"
              key={item}
              className={timeframe === item ? 'active' : ''}
              onClick={() => onTimeframeChange(item)}
            >
              {item.toUpperCase()}
            </button>
          ))}
        </div>

        <div className="selector-group">
          <span className="selector-label">Chart</span>
          <button type="button" className={chartType === 'candlestick' ? 'active' : ''} onClick={() => setChartType('candlestick')}>
            Candlestick
          </button>
          <button type="button" className={chartType === 'line' ? 'active' : ''} onClick={() => setChartType('line')}>
            Line
          </button>
        </div>
      </div>

      <div ref={wrapperRef} className="trading-chart-shell mt-4">
        <div ref={chartRef} className="chart-box price-full"></div>
        <div ref={tooltipRef} className="trading-tooltip"></div>
      </div>
    </div>
  )
}

export default memo(TradingViewChartPanel)
