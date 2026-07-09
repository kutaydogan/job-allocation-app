import { ButtonHTMLAttributes, HTMLAttributes, InputHTMLAttributes, TextareaHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';
export function Card(props: HTMLAttributes<HTMLDivElement>) { return <div {...props} className={cn('rounded-2xl border bg-white p-6 shadow-sm', props.className)} />; }
export function Button(props: ButtonHTMLAttributes<HTMLButtonElement>) { return <button {...props} className={cn('rounded-xl bg-brand px-4 py-2 font-semibold text-white hover:bg-blue-700 disabled:opacity-50', props.className)} />; }
export function Input(props: InputHTMLAttributes<HTMLInputElement>) { return <input {...props} className={cn('w-full rounded-xl border px-3 py-2', props.className)} />; }
export function Textarea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) { return <textarea {...props} className={cn('w-full rounded-xl border px-3 py-2 font-mono text-sm', props.className)} />; }
