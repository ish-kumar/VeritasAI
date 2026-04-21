"use client";

import { useEffect, useRef, useCallback, useTransition } from "react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import {
    Scale,
    FileText,
    Shield,
    AlertTriangle,
    ArrowUpIcon,
    Paperclip,
    SendIcon,
    XIcon,
    LoaderIcon,
    Command,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import * as React from "react"

interface UseAutoResizeTextareaProps {
    minHeight: number;
    maxHeight?: number;
}

function useAutoResizeTextarea({
    minHeight,
    maxHeight,
}: UseAutoResizeTextareaProps) {
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const adjustHeight = useCallback(
        (reset?: boolean) => {
            const textarea = textareaRef.current;
            if (!textarea) return;

            if (reset) {
                textarea.style.height = `${minHeight}px`;
                return;
            }

            textarea.style.height = `${minHeight}px`;
            const newHeight = Math.max(
                minHeight,
                Math.min(
                    textarea.scrollHeight,
                    maxHeight ?? Number.POSITIVE_INFINITY
                )
            );

            textarea.style.height = `${newHeight}px`;
        },
        [minHeight, maxHeight]
    );

    useEffect(() => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = `${minHeight}px`;
        }
    }, [minHeight]);

    useEffect(() => {
        const handleResize = () => adjustHeight();
        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, [adjustHeight]);

    return { textareaRef, adjustHeight };
}

interface CommandSuggestion {
    icon: React.ReactNode;
    label: string;
    description: string;
    prefix: string;
}

interface TextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  containerClassName?: string;
  showRing?: boolean;
}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, containerClassName, showRing = true, ...props }, ref) => {
    const [isFocused, setIsFocused] = React.useState(false);
    
    return (
      <div className={cn(
        "relative",
        containerClassName
      )}>
        <textarea
          className={cn(
            "flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm",
            "transition-all duration-200 ease-in-out",
            "placeholder:text-muted-foreground",
            "disabled:cursor-not-allowed disabled:opacity-50",
            showRing ? "focus-visible:outline-none focus-visible:ring-0 focus-visible:ring-offset-0" : "",
            className
          )}
          ref={ref}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          {...props}
        />
        
        {showRing && isFocused && (
          <motion.span 
            className="absolute inset-0 rounded-md pointer-events-none ring-2 ring-offset-0 ring-blue-500/30"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          />
        )}
      </div>
    )
  }
)
Textarea.displayName = "Textarea"

interface LegalQueryInputProps {
    value: string;
    onChange: (value: string) => void;
    onSubmit: () => void;
    isLoading?: boolean;
    disabled?: boolean;
    placeholder?: string;
    onJurisdictionSelect?: (jurisdiction: string) => void;
}

export function LegalQueryInput({
    value,
    onChange,
    onSubmit,
    isLoading = false,
    disabled = false,
    placeholder = "Ask a legal question...",
    onJurisdictionSelect,
}: LegalQueryInputProps) {
    const [attachments, setAttachments] = useState<string[]>([]);
    const [activeSuggestion, setActiveSuggestion] = useState<number>(-1);
    const [showCommandPalette, setShowCommandPalette] = useState(false);
    const { textareaRef, adjustHeight } = useAutoResizeTextarea({
        minHeight: 60,
        maxHeight: 200,
    });
    const [inputFocused, setInputFocused] = useState(false);
    const commandPaletteRef = useRef<HTMLDivElement>(null);

    // Legal-specific command suggestions (not generic AI chat)
    const commandSuggestions: CommandSuggestion[] = [
        { 
            icon: <Scale className="w-4 h-4" />, 
            label: "Specify Jurisdiction", 
            description: "Filter by legal jurisdiction", 
            prefix: "/jurisdiction" 
        },
        { 
            icon: <FileText className="w-4 h-4" />, 
            label: "Cite Sources", 
            description: "Require citation verification", 
            prefix: "/cite" 
        },
        { 
            icon: <Shield className="w-4 h-4" />, 
            label: "Risk Assessment", 
            description: "Focus on risk factors", 
            prefix: "/risk" 
        },
        { 
            icon: <AlertTriangle className="w-4 h-4" />, 
            label: "Counter-Arguments", 
            description: "Show adversarial analysis", 
            prefix: "/counter" 
        },
    ];

    useEffect(() => {
        if (value.startsWith('/') && !value.includes(' ')) {
            setShowCommandPalette(true);
            
            const matchingSuggestionIndex = commandSuggestions.findIndex(
                (cmd) => cmd.prefix.startsWith(value)
            );
            
            if (matchingSuggestionIndex >= 0) {
                setActiveSuggestion(matchingSuggestionIndex);
            } else {
                setActiveSuggestion(-1);
            }
        } else {
            setShowCommandPalette(false);
        }
    }, [value]);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            const target = event.target as Node;
            const commandButton = document.querySelector('[data-command-button]');
            
            if (commandPaletteRef.current && 
                !commandPaletteRef.current.contains(target) && 
                !commandButton?.contains(target)) {
                setShowCommandPalette(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (showCommandPalette) {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                setActiveSuggestion(prev => 
                    prev < commandSuggestions.length - 1 ? prev + 1 : 0
                );
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                setActiveSuggestion(prev => 
                    prev > 0 ? prev - 1 : commandSuggestions.length - 1
                );
            } else if (e.key === 'Tab' || e.key === 'Enter') {
                e.preventDefault();
                if (activeSuggestion >= 0) {
                    const selectedCommand = commandSuggestions[activeSuggestion];
                    onChange(selectedCommand.prefix + ' ');
                    setShowCommandPalette(false);
                }
            } else if (e.key === 'Escape') {
                e.preventDefault();
                setShowCommandPalette(false);
            }
        } else if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            if (value.trim()) {
                onSubmit();
            }
        }
    };

    const selectCommandSuggestion = (index: number) => {
        const selectedCommand = commandSuggestions[index];
        onChange(selectedCommand.prefix + ' ');
        setShowCommandPalette(false);
    };

    return (
        <div className="w-full relative pb-8">
            <motion.div 
                className="relative z-10"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, ease: "easeOut" }}
            >
                {/* Main Input Container - Clean, no AI slop */}
                <motion.div 
                    className="relative backdrop-blur-xl bg-surface/50 rounded-2xl border border-white/10 shadow-xl"
                    initial={{ scale: 0.98 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.1 }}
                >
                    <div className="p-4">
                        <Textarea
                            ref={textareaRef}
                            value={value}
                            onChange={(e) => {
                                onChange(e.target.value);
                                adjustHeight();
                            }}
                            onKeyDown={handleKeyDown}
                            onFocus={() => setInputFocused(true)}
                            onBlur={() => setInputFocused(false)}
                            placeholder={placeholder}
                            disabled={disabled || isLoading}
                            aria-label="Legal query input"
                            containerClassName="w-full"
                            className={cn(
                                "w-full px-4 py-3",
                                "resize-none",
                                "bg-transparent",
                                "border-none",
                                "text-white/90 text-base",
                                "focus:outline-none",
                                "placeholder:text-secondary",
                                "min-h-[60px]"
                            )}
                            style={{
                                overflow: "hidden",
                            }}
                            showRing={false}
                        />
                    </div>

                    {/* Attachments Display */}
                    <AnimatePresence>
                        {attachments.length > 0 && (
                            <motion.div 
                                className="px-4 pb-3 flex gap-2 flex-wrap"
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: "auto" }}
                                exit={{ opacity: 0, height: 0 }}
                            >
                                {attachments.map((file, index) => (
                                    <motion.div
                                        key={index}
                                        className="flex items-center gap-2 text-xs bg-white/[0.03] py-1.5 px-3 rounded-lg text-secondary border border-white/5"
                                        initial={{ opacity: 0, scale: 0.9 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        exit={{ opacity: 0, scale: 0.9 }}
                                    >
                                        <span>{file}</span>
                                        <button 
                                            onClick={() => setAttachments(prev => prev.filter((_, i) => i !== index))}
                                            className="text-white/40 hover:text-white transition-colors"
                                        >
                                            <XIcon className="w-3 h-3" />
                                        </button>
                                    </motion.div>
                                ))}
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Bottom Toolbar */}
                    <div className="p-4 border-t border-white/[0.05] flex items-center justify-between gap-4">
                        <div className="flex items-center gap-2">
                            {/* Command Button */}
                            <motion.button
                                type="button"
                                data-command-button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    setShowCommandPalette(prev => !prev);
                                }}
                                whileTap={{ scale: 0.94 }}
                                className={cn(
                                    "p-2 text-secondary hover:text-white rounded-lg transition-colors relative group",
                                    showCommandPalette && "bg-blue-500/10 text-blue-400"
                                )}
                                title="Legal commands"
                            >
                                <Command className="w-4 h-4" />
                                <motion.span
                                    className="absolute inset-0 bg-white/[0.05] rounded-lg opacity-0 group-hover:opacity-100 transition-opacity"
                                />
                            </motion.button>

                            {/* Helper Text */}
                            <span className="text-xs text-muted">
                                {showCommandPalette ? "Select a command" : "Press / for commands"}
                            </span>
                        </div>
                        
                        {/* Submit Button */}
                        <motion.button
                            type="button"
                            onClick={onSubmit}
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            disabled={isLoading || !value.trim() || disabled}
                            className={cn(
                                "px-5 py-2.5 rounded-lg text-sm font-medium transition-all",
                                "flex items-center gap-2",
                                value.trim() && !isLoading && !disabled
                                    ? "bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-500/20"
                                    : "bg-white/[0.05] text-secondary cursor-not-allowed"
                            )}
                        >
                            {isLoading ? (
                                <LoaderIcon className="w-4 h-4 animate-spin" />
                            ) : (
                                <SendIcon className="w-4 h-4" />
                            )}
                            <span>Query</span>
                        </motion.button>
                    </div>
                </motion.div>

                {/* Command Palette - Appears BELOW input to prevent overlap */}
                <AnimatePresence>
                    {showCommandPalette && (
                        <motion.div 
                            ref={commandPaletteRef}
                            className="mt-2 backdrop-blur-xl bg-surface border border-white/10 rounded-xl shadow-2xl overflow-hidden relative z-50"
                            initial={{ opacity: 0, y: -8 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -8 }}
                            transition={{ duration: 0.2 }}
                        >
                            <div className="py-2 px-2">
                                {commandSuggestions.map((suggestion, index) => (
                                    <motion.div
                                        key={suggestion.prefix}
                                        className={cn(
                                            "flex items-center gap-3 px-4 py-3 text-sm transition-colors cursor-pointer rounded-lg",
                                            activeSuggestion === index 
                                                ? "bg-blue-500/10 text-white border-l-2 border-blue-500 ml-0.5" 
                                                : "text-secondary hover:bg-white/5"
                                        )}
                                        onClick={() => selectCommandSuggestion(index)}
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        transition={{ delay: index * 0.03 }}
                                    >
                                        <div className="w-6 h-6 flex items-center justify-center text-blue-400">
                                            {suggestion.icon}
                                        </div>
                                        <div className="flex-1">
                                            <div className="font-medium">{suggestion.label}</div>
                                            <div className="text-xs text-muted">{suggestion.description}</div>
                                        </div>
                                        <code className="text-xs text-muted font-mono">{suggestion.prefix}</code>
                                    </motion.div>
                                ))}
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Quick Actions - Legal-specific, clear spacing */}
                <motion.div 
                    className="flex flex-wrap items-center justify-center gap-3 mt-6 mb-2 relative z-10"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                >
                    {commandSuggestions.map((suggestion, index) => (
                        <motion.button
                            key={suggestion.prefix}
                            onClick={() => selectCommandSuggestion(index)}
                            className="flex items-center gap-2 px-4 py-2 bg-white/[0.02] hover:bg-white/[0.08] rounded-lg text-xs text-secondary hover:text-white transition-all border border-white/5 hover:border-white/10"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.4 + index * 0.05 }}
                            whileHover={{ scale: 1.03 }}
                            whileTap={{ scale: 0.97 }}
                        >
                            {suggestion.icon}
                            <span>{suggestion.label}</span>
                        </motion.button>
                    ))}
                </motion.div>
            </motion.div>

            {/* Typing Indicator - In normal document flow */}
            <AnimatePresence>
                {isLoading && (
                    <motion.div 
                        className="mt-6 flex justify-center"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                        transition={{ duration: 0.3 }}
                    >
                        <div className="backdrop-blur-xl bg-surface border border-white/10 rounded-full px-5 py-3 shadow-xl inline-flex items-center gap-3">
                            <div className="w-8 h-7 rounded-full bg-blue-500/10 flex items-center justify-center">
                                <Scale className="w-4 h-4 text-blue-400" />
                            </div>
                            <div className="flex items-center gap-2 text-sm text-secondary">
                                <span>Analyzing</span>
                                <TypingDots />
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

function TypingDots() {
    return (
        <div className="flex items-center ml-1">
            {[1, 2, 3].map((dot) => (
                <motion.div
                    key={dot}
                    className="w-1.5 h-1.5 bg-blue-400 rounded-full mx-0.5"
                    initial={{ opacity: 0.3 }}
                    animate={{ 
                        opacity: [0.3, 0.9, 0.3],
                        scale: [0.85, 1.1, 0.85]
                    }}
                    transition={{
                        duration: 1.2,
                        repeat: Infinity,
                        delay: dot * 0.15,
                        ease: "easeInOut",
                    }}
                />
            ))}
        </div>
    );
}
