import { useState } from 'react'

interface ChatInputProps {
  onSend: (msg: string) => void | Promise<void>
  disabled?: boolean
  // optional class overrides for container, input and button
  formClassName?: string
  inputClassName?: string
  buttonClassName?: string
}

export default function ChatInput({ onSend, disabled = false, formClassName = 'flex gap-2', inputClassName = 'flex-1 border p-2 rounded-xl text-[#260000]', buttonClassName = 'bg-[#DEA193] text-white px-3 rounded-xl' }: ChatInputProps) {
  const [value, setValue] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!value.trim() || disabled) return;

    const message = value;
    setValue(""); // Clear immediately

    try {
      await onSend(message);
    } catch (error) {
      console.error('Failed to send message:', error);
      setValue(message); // Restore message on error
    }
  }

  return (
    <form onSubmit={handleSubmit} className={formClassName}>
      <input
        className={`${inputClassName} disabled:bg-gray-100 disabled:cursor-not-allowed`}
        placeholder={disabled ? "Sending..." : "Ask a skincare question..."}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        disabled={disabled}
      />
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        className={`${buttonClassName} disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors`}
      >
        {disabled ? "Sending..." : "Send"}
      </button>
    </form>
  );
}