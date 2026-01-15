export default function Card({ children }: { children: React.ReactNode }) {
  return <div className="p-4 rounded shadow bg-white">{children}</div>
}

/*

Notes for my teammates:

This is a reusable Card component that can be used to wrap content in a styled container.

*/