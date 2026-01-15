export default function Badge({ children }: { children: string }) {
  return <span className="inline-block bg-gray-200 px-2 py-1 rounded text-sm">{children}</span>
}

/*

Notes for my teammates:

This component is responsible for rendering a badge with a light gray background and rounded corners.

What is a badge?

A badge is a small UI element that displays a status or category label. 
Badges are often used to highlight important information, such as notifications, user status, or item categories.

Why use a badge?

Badges help to draw attention to specific information and make it easier for users to quickly identify important details.
They can also enhance the visual appeal of the UI by adding color and contrast.

How to use this component?

To use the Badge component, simply import it into your React component and pass the desired text as children. For example:

import Badge from './Badge'

function Example() {
  return <Badge>New</Badge>
}

This will render a badge with the text "New".

Feel free to customize the styles as needed to match the overall design of the application.

Idea: I was thinking we could use this badge component to indicate new messages in the chat or to highlight important sections in the intake form.
But overall we can delete this is you guys want, I just thought it might be useful.

*/