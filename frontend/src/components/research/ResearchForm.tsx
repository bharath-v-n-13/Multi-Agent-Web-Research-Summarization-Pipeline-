import React from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { SearchCode, FileText, Sliders, Layers } from "lucide-react";
import Button from "../common/Button";
import type { ResearchRequest } from "../../types/research";

const formSchema = z.object({
  topic: z
    .string()
    .min(5, "Topic must be at least 5 characters.")
    .max(200, "Topic cannot exceed 200 characters."),
  depth: z.enum(["shallow", "moderate", "deep"]),
  max_sources: z
    .number()
    .min(5, "Minimum 5 sources required.")
    .max(50, "Maximum 50 sources allowed."),
  output_format: z.enum(["markdown", "pdf", "json"]),
});

type FormValues = z.infer<typeof formSchema>;

interface ResearchFormProps {
  onSubmit: (values: ResearchRequest) => void;
  isLoading: boolean;
}

export const ResearchForm: React.FC<ResearchFormProps> = ({ onSubmit, isLoading }) => {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      topic: "",
      depth: "moderate",
      max_sources: 20,
      output_format: "markdown",
    },
  });

  const watchMaxSources = watch("max_sources");

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-6 rounded-2xl border border-slate-200/80 dark:border-slate-800/80 bg-white dark:bg-slate-900 p-6 shadow-soft"
    >
      {/* Title */}
      <div className="flex items-center space-x-2 border-b border-slate-100 dark:border-slate-800 pb-4">
        <SearchCode className="h-5 w-5 text-brand-teal" />
        <h2 className="text-base font-semibold text-slate-950 dark:text-slate-50">
          Research Configuration
        </h2>
      </div>

      {/* Topic input */}
      <div className="space-y-2">
        <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 flex items-center justify-between">
          <span>RESEARCH TOPIC</span>
          <span className="text-[10px] text-slate-400 font-medium">5-200 characters</span>
        </label>
        <textarea
          {...register("topic")}
          disabled={isLoading}
          rows={3}
          placeholder="e.g. Future of Quantum Computing, Superconducting Qubits in NISQ era, solid-state battery densities..."
          className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-transparent px-3.5 py-2.5 text-sm outline-none focus:border-brand-navy dark:focus:border-slate-500 disabled:opacity-50 transition-all placeholder:text-slate-400 text-slate-900 dark:text-slate-100"
        />
        {errors.topic && (
          <p className="text-xs font-medium text-rose-500 mt-1">{errors.topic.message}</p>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Depth dropdown */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 flex items-center space-x-1.5">
            <Layers className="h-3.5 w-3.5 text-slate-400" />
            <span>RESEARCH DEPTH</span>
          </label>
          <select
            {...register("depth")}
            disabled={isLoading}
            className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3.5 py-2.5 text-sm outline-none focus:border-brand-navy dark:focus:border-slate-500 disabled:opacity-50 text-slate-900 dark:text-slate-100 transition-all appearance-none cursor-pointer"
          >
            <option value="shallow">Shallow (Breadth First)</option>
            <option value="moderate">Moderate (Balanced)</option>
            <option value="deep">Deep (Iterative Deepening)</option>
          </select>
        </div>

        {/* Output format dropdown */}
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-700 dark:text-slate-300 flex items-center space-x-1.5">
            <FileText className="h-3.5 w-3.5 text-slate-400" />
            <span>EXPORT FORMAT</span>
          </label>
          <select
            {...register("output_format")}
            disabled={isLoading}
            className="w-full rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3.5 py-2.5 text-sm outline-none focus:border-brand-navy dark:focus:border-slate-500 disabled:opacity-50 text-slate-900 dark:text-slate-100 transition-all appearance-none cursor-pointer"
          >
            <option value="markdown">Markdown (.md)</option>
            <option value="pdf">Typeset PDF (.pdf)</option>
            <option value="json">JSON (.json)</option>
          </select>
        </div>
      </div>

      {/* Max sources slider */}
      <div className="space-y-2">
        <div className="flex justify-between items-center text-xs font-semibold text-slate-700 dark:text-slate-300">
          <span className="flex items-center space-x-1.5">
            <Sliders className="h-3.5 w-3.5 text-slate-400" />
            <span>MAXIMUM UNIQUE SOURCES</span>
          </span>
          <span className="rounded bg-slate-100 dark:bg-slate-800 px-2 py-0.5 font-mono text-[11px] text-brand-navy dark:text-slate-300">
            {watchMaxSources} sources
          </span>
        </div>
        <div className="flex items-center space-x-4 pt-1">
          <input
            type="range"
            min={5}
            max={50}
            step={1}
            disabled={isLoading}
            {...register("max_sources", { valueAsNumber: true })}
            className="h-1.5 w-full cursor-pointer rounded-lg bg-slate-100 dark:bg-slate-800 accent-brand-navy dark:accent-slate-100 outline-none disabled:opacity-50"
          />
        </div>
        <div className="flex justify-between text-[10px] font-medium text-slate-400 font-mono">
          <span>5</span>
          <span>25</span>
          <span>50</span>
        </div>
      </div>

      {/* Submit Button */}
      <Button
        type="submit"
        isLoading={isLoading}
        disabled={isLoading}
        className="w-full py-2.5 rounded-xl text-sm font-semibold tracking-wide"
      >
        Compile Autonomous Research
      </Button>
    </form>
  );
};
export default ResearchForm;
