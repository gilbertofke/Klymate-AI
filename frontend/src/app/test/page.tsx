export default function TestPage() {
  return (
    <div style={{ padding: '20px', backgroundColor: 'white', minHeight: '100vh' }}>
      <h1>Test Page</h1>
      <p>If you can see this, Next.js routing is working!</p>
      <button onClick={() => alert('Button works!')}>
        Click me
      </button>
    </div>
  )
}