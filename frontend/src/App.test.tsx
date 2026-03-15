import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders the application title', () => {
    render(<App />)
    const titleElements = screen.getAllByText(/Intelli-Credit/i)
    expect(titleElements.length).toBeGreaterThan(0)
  })

  it('renders the hero message', () => {
    render(<App />)
    const heroElement = screen.getByText(/Best Financing Solutions/i)
    expect(heroElement).toBeInTheDocument()
  })
})
