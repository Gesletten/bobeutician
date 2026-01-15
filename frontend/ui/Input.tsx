export default function Input(props: any) {
  return <input {...props} className={(props.className || '') + ' border p-2 rounded'} />
}

/*

Notes for my teammates:

This is a reusable Input component that can be used throughout the application.

It accepts all standard input props and applies some default styling.

*/