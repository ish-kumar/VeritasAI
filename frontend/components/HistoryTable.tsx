"use client"

import * as React from "react"
import {
  ColumnDef,
  ColumnFiltersState,
  SortingState,
  VisibilityState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table"
import { ArrowUpDown, ChevronDown, MoreHorizontal, Trash2, Clock, Search, Copy, ExternalLink, AlertTriangle } from "lucide-react"
import Link from "next/link"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

interface QueryHistoryItem {
  id: string
  query: string
  timestamp: number
  answered: boolean
  confidence?: number
  risk?: string
}

interface HistoryTableProps {
  history: QueryHistoryItem[]
  onDelete: (id: string) => void
  formatDate: (timestamp: number) => string
}

export function HistoryTable({ history, onDelete, formatDate }: HistoryTableProps) {
  const [sorting, setSorting] = React.useState<SortingState>([
    { id: "timestamp", desc: true } // Most recent first by default
  ])
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])
  const [columnVisibility, setColumnVisibility] = React.useState<VisibilityState>({})
  const [rowSelection, setRowSelection] = React.useState({})
  const [statusFilter, setStatusFilter] = React.useState<string>("all")
  const [riskFilter, setRiskFilter] = React.useState<string>("all")
  const [bulkDeleteDialogOpen, setBulkDeleteDialogOpen] = React.useState(false)

  const getRiskColor = (risk?: string) => {
    if (!risk) return "text-muted"
    switch (risk) {
      case 'low': return 'text-emerald-400'
      case 'medium': return 'text-amber-400'
      case 'high': return 'text-orange-400'
      case 'critical': return 'text-rose-400'
      default: return 'text-muted'
    }
  }

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return "text-muted"
    if (confidence >= 80) return "text-emerald-400"
    if (confidence >= 60) return "text-amber-400"
    return "text-rose-400"
  }

  const columns: ColumnDef<QueryHistoryItem>[] = [
    {
      id: "select",
      header: ({ table }) => (
        <Checkbox
          checked={
            table.getIsAllPageRowsSelected() ||
            (table.getIsSomePageRowsSelected() && "indeterminate")
          }
          onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
          aria-label="Select all"
        />
      ),
      cell: ({ row }) => (
        <Checkbox
          checked={row.getIsSelected()}
          onCheckedChange={(value) => row.toggleSelected(!!value)}
          aria-label="Select row"
        />
      ),
      enableSorting: false,
      enableHiding: false,
    },
    {
      accessorKey: "query",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="hover:bg-white/5"
          >
            Query
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        const query = row.getValue("query") as string
        return (
          <Link 
            href={`/query?q=${encodeURIComponent(query)}`}
            className="text-text-primary hover:text-blue-400 transition-colors line-clamp-2 max-w-md block"
            title={query}
          >
            {query}
          </Link>
        )
      },
    },
    {
      accessorKey: "timestamp",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="hover:bg-white/5"
          >
            <Clock className="mr-2 h-4 w-4" />
            Time
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        const timestamp = row.getValue("timestamp") as number
        const date = new Date(timestamp)
        return (
          <div className="text-secondary">
            <div className="text-sm">{formatDate(timestamp)}</div>
            <div className="text-xs text-muted">{date.toLocaleString()}</div>
          </div>
        )
      },
    },
    {
      accessorKey: "answered",
      header: "Status",
      cell: ({ row }) => {
        const answered = row.getValue("answered") as boolean
        return answered ? (
          <span className="px-2 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-medium">
            Answered
          </span>
        ) : (
          <span className="px-2 py-1 rounded-full bg-rose-500/20 text-rose-400 text-xs font-medium">
            Refused
          </span>
        )
      },
      filterFn: (row, id, value) => {
        if (value === "all") return true
        const answered = row.getValue(id) as boolean
        return value === "answered" ? answered : !answered
      },
    },
    {
      accessorKey: "confidence",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="hover:bg-white/5"
          >
            Confidence
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        const confidence = row.getValue("confidence") as number | undefined
        if (confidence === undefined) return <span className="text-muted">—</span>
        
        return (
          <div className={`font-medium ${getConfidenceColor(confidence)}`}>
            {confidence.toFixed(1)}%
          </div>
        )
      },
      sortingFn: (rowA, rowB, columnId) => {
        const a = rowA.getValue(columnId) as number | undefined
        const b = rowB.getValue(columnId) as number | undefined
        if (a === undefined) return 1
        if (b === undefined) return -1
        return a - b
      },
    },
    {
      accessorKey: "risk",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="hover:bg-white/5"
          >
            Risk
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        const risk = row.getValue("risk") as string | undefined
        if (!risk) return <span className="text-muted">—</span>
        
        return (
          <div className={`text-xs font-medium uppercase ${getRiskColor(risk)}`}>
            {risk}
          </div>
        )
      },
      sortingFn: (rowA, rowB, columnId) => {
        const riskOrder: Record<string, number> = { low: 0, medium: 1, high: 2, critical: 3 }
        const a = rowA.getValue(columnId) as string | undefined
        const b = rowB.getValue(columnId) as string | undefined
        if (!a) return 1
        if (!b) return -1
        return riskOrder[a] - riskOrder[b]
      },
      filterFn: (row, id, value) => {
        if (value === "all") return true
        const risk = row.getValue(id) as string | undefined
        return risk === value
      },
    },
    {
      id: "actions",
      enableHiding: false,
      cell: ({ row }) => {
        const item = row.original

        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0 hover:bg-white/5">
                <span className="sr-only">Open menu</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="bg-surface border-white/10">
              <DropdownMenuLabel className="text-text-primary">Actions</DropdownMenuLabel>
              <DropdownMenuItem
                asChild
                className="hover:bg-white/5 text-secondary cursor-pointer"
              >
                <Link href={`/query?q=${encodeURIComponent(item.query)}`}>
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Re-run Query
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => {
                  navigator.clipboard.writeText(item.query)
                  toast.success('Copied to clipboard', {
                    description: item.query.length > 50 ? item.query.substring(0, 50) + '...' : item.query
                  })
                }}
                className="hover:bg-white/5 text-secondary"
              >
                <Copy className="mr-2 h-4 w-4" />
                Copy Query Text
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-white/10" />
              <DropdownMenuItem
                onClick={() => onDelete(item.id)}
                className="hover:bg-rose-500/10 text-rose-400 focus:text-rose-400"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ]

  // Apply custom filters
  const filteredData = React.useMemo(() => {
    let filtered = history

    if (statusFilter !== "all") {
      filtered = filtered.filter(item => 
        statusFilter === "answered" ? item.answered : !item.answered
      )
    }

    if (riskFilter !== "all") {
      filtered = filtered.filter(item => item.risk === riskFilter)
    }

    return filtered
  }, [history, statusFilter, riskFilter])

  const table = useReactTable({
    data: filteredData,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
    },
  })

  const selectedCount = table.getFilteredSelectedRowModel().rows.length

  return (
    <div className="w-full space-y-4">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-4">
        {/* Search */}
        <Input
          placeholder="Search queries..."
          value={(table.getColumn("query")?.getFilterValue() as string) ?? ""}
          onChange={(event) =>
            table.getColumn("query")?.setFilterValue(event.target.value)
          }
          className="max-w-sm bg-surface border-white/10 text-text-primary placeholder:text-muted focus-visible:ring-blue-500/30"
        />

        {/* Status Filter */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="bg-surface border-white/10 text-text-primary hover:bg-white/5">
              Status: {statusFilter === "all" ? "All" : statusFilter === "answered" ? "Answered" : "Refused"}
              <ChevronDown className="ml-2 h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="bg-surface border-white/10">
            <DropdownMenuItem onClick={() => setStatusFilter("all")} className="hover:bg-white/5 text-secondary">
              All
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setStatusFilter("answered")} className="hover:bg-white/5 text-secondary">
              Answered
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setStatusFilter("refused")} className="hover:bg-white/5 text-secondary">
              Refused
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Risk Filter */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="bg-surface border-white/10 text-text-primary hover:bg-white/5">
              Risk: {riskFilter === "all" ? "All" : riskFilter}
              <ChevronDown className="ml-2 h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="bg-surface border-white/10">
            <DropdownMenuItem onClick={() => setRiskFilter("all")} className="hover:bg-white/5 text-secondary">
              All
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setRiskFilter("low")} className="hover:bg-white/5 text-emerald-400">
              Low
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setRiskFilter("medium")} className="hover:bg-white/5 text-amber-400">
              Medium
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setRiskFilter("high")} className="hover:bg-white/5 text-orange-400">
              High
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setRiskFilter("critical")} className="hover:bg-white/5 text-rose-400">
              Critical
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
        
        {/* Bulk Delete */}
        {selectedCount > 0 && (
          <Button
            variant="destructive"
            size="sm"
            onClick={() => setBulkDeleteDialogOpen(true)}
            className="bg-rose-500/20 hover:bg-rose-500/30 text-rose-400 border border-rose-500/30"
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Delete {selectedCount}
          </Button>
        )}

        <div className="flex-1" />

        {/* Column Visibility */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="bg-surface border-white/10 text-text-primary hover:bg-white/5">
              Columns <ChevronDown className="ml-2 h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="bg-surface border-white/10">
            {table
              .getAllColumns()
              .filter((column) => column.getCanHide())
              .map((column) => {
                return (
                  <DropdownMenuCheckboxItem
                    key={column.id}
                    className="capitalize hover:bg-white/5 text-secondary"
                    checked={column.getIsVisible()}
                    onCheckedChange={(value) =>
                      column.toggleVisibility(!!value)
                    }
                  >
                    {column.id}
                  </DropdownMenuCheckboxItem>
                )
              })}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {/* Active Filters Display */}
      {(statusFilter !== "all" || riskFilter !== "all") && (
        <div className="flex items-center gap-2 text-sm">
          <span className="text-muted">Active filters:</span>
          {statusFilter !== "all" && (
            <span className="px-2 py-1 bg-blue-500/10 text-blue-400 rounded-md">
              Status: {statusFilter}
            </span>
          )}
          {riskFilter !== "all" && (
            <span className={`px-2 py-1 bg-white/5 rounded-md ${getRiskColor(riskFilter)}`}>
              Risk: {riskFilter}
            </span>
          )}
          <button
            onClick={() => {
              setStatusFilter("all")
              setRiskFilter("all")
            }}
            className="text-xs text-blue-400 hover:underline"
          >
            Clear filters
          </button>
        </div>
      )}

      {/* Table */}
      <div className="rounded-xl border border-white/10 glass overflow-hidden">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id} className="border-white/10 hover:bg-white/5">
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id} className="text-muted-foreground">
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext(),
                          )}
                    </TableHead>
                  )
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                  className="border-white/10 hover:bg-white/5 data-[state=selected]:bg-blue-500/10"
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  <div className="text-muted">
                    {columnFilters.length > 0 || statusFilter !== "all" || riskFilter !== "all"
                      ? "No queries match your filters."
                      : "No query history found."}
                  </div>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <div className="flex-1 text-sm text-muted">
          {selectedCount > 0 ? (
            <span>
              {selectedCount} of {table.getFilteredRowModel().rows.length} row(s) selected.
            </span>
          ) : (
            <span>
              {table.getFilteredRowModel().rows.length} quer{table.getFilteredRowModel().rows.length === 1 ? 'y' : 'ies'} total
            </span>
          )}
        </div>
        <div className="flex items-center gap-6">
          <div className="text-sm text-muted">
            Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount() || 1}
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
              className="bg-surface border-white/10 text-text-primary hover:bg-white/5 disabled:opacity-50"
            >
              Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
              className="bg-surface border-white/10 text-text-primary hover:bg-white/5 disabled:opacity-50"
            >
              Next
            </Button>
          </div>
        </div>
      </div>

      {/* Bulk Delete Confirmation */}
      <AlertDialog open={bulkDeleteDialogOpen} onOpenChange={setBulkDeleteDialogOpen}>
        <AlertDialogContent className="bg-surface border-white/10">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-text-primary flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-rose-400" />
              Delete {selectedCount} Quer{selectedCount === 1 ? 'y' : 'ies'}?
            </AlertDialogTitle>
            <AlertDialogDescription className="text-secondary">
              <div className="space-y-3 mt-4">
                <p>You are about to permanently delete {selectedCount} quer{selectedCount === 1 ? 'y' : 'ies'} from your history. This action cannot be undone.</p>
                <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                  <p className="text-sm text-muted">
                    This will only delete the local browser history, not the actual query results.
                  </p>
                </div>
              </div>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-surface border-white/10 text-text-primary hover:bg-white/5">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                const selectedRows = table.getFilteredSelectedRowModel().rows
                const count = selectedRows.length
                selectedRows.forEach(row => onDelete(row.original.id))
                table.resetRowSelection()
                toast.success(`Deleted ${count} quer${count === 1 ? 'y' : 'ies'}`, {
                  description: 'Query history updated'
                })
              }}
              className="bg-rose-600 hover:bg-rose-500 text-white"
            >
              Delete {selectedCount}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
