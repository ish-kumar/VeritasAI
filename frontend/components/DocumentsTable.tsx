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
import { ArrowUpDown, ChevronDown, MoreHorizontal, Trash2, FileText, File, Database, Loader2, AlertTriangle } from "lucide-react"
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
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
import { DocumentInfo } from "@/lib/api"

interface DocumentsTableProps {
  documents: DocumentInfo[]
  onDelete: (documentId: string) => Promise<void>
  deletingId: string | null
}

export function DocumentsTable({ documents, onDelete, deletingId }: DocumentsTableProps) {
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])
  const [columnVisibility, setColumnVisibility] = React.useState<VisibilityState>({})
  const [rowSelection, setRowSelection] = React.useState({})
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false)
  const [documentToDelete, setDocumentToDelete] = React.useState<DocumentInfo | null>(null)
  const [bulkDeleteDialogOpen, setBulkDeleteDialogOpen] = React.useState(false)

  const getDocIcon = (docType: string) => {
    if (docType === 'pdf') return <File className="w-4 h-4 text-rose-400" />
    if (docType === 'docx') return <File className="w-4 h-4 text-blue-400" />
    return <FileText className="w-4 h-4 text-emerald-400" />
  }

  const columns: ColumnDef<DocumentInfo>[] = [
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
      accessorKey: "document_id",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="hover:bg-white/5"
          >
            Document ID
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => (
        <div className="font-mono text-sm text-text-primary">{row.getValue("document_id")}</div>
      ),
    },
    {
      accessorKey: "doc_type",
      header: "Type",
      cell: ({ row }) => {
        const docType = row.getValue("doc_type") as string
        return (
          <div className="flex items-center gap-2">
            {getDocIcon(docType)}
            <span className="uppercase text-xs font-medium text-secondary">{docType}</span>
          </div>
        )
      },
    },
    {
      accessorKey: "chunk_count",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="hover:bg-white/5"
          >
            <Database className="mr-2 h-4 w-4 text-blue-400" />
            Chunks
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => {
        return <div className="text-center font-medium text-text-primary">{row.getValue("chunk_count")}</div>
      },
    },
    {
      accessorKey: "jurisdiction",
      header: ({ column }) => {
        return (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
            className="hover:bg-white/5"
          >
            Jurisdiction
            <ArrowUpDown className="ml-2 h-4 w-4" />
          </Button>
        )
      },
      cell: ({ row }) => <div className="text-secondary">{row.getValue("jurisdiction")}</div>,
    },
    {
      id: "actions",
      enableHiding: false,
      cell: ({ row }) => {
        const document = row.original
        const isDeleting = deletingId === document.document_id

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
                onClick={() => {
                  navigator.clipboard.writeText(document.document_id)
                  toast.success('Copied to clipboard', {
                    description: `Document ID: ${document.document_id}`
                  })
                }}
                className="hover:bg-white/5 text-secondary"
              >
                Copy Document ID
              </DropdownMenuItem>
              <DropdownMenuSeparator className="bg-white/10" />
              <DropdownMenuItem
                onClick={() => {
                  setDocumentToDelete(document)
                  setDeleteDialogOpen(true)
                }}
                disabled={isDeleting}
                className="hover:bg-rose-500/10 text-rose-400 focus:text-rose-400"
              >
                {isDeleting ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Deleting...
                  </>
                ) : (
                  <>
                    <Trash2 className="mr-2 h-4 w-4" />
                    Delete
                  </>
                )}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ]

  const table = useReactTable({
    data: documents,
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
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-4 flex-1">
          {/* Search */}
          <Input
            placeholder="Filter by document ID..."
            value={(table.getColumn("document_id")?.getFilterValue() as string) ?? ""}
            onChange={(event) =>
              table.getColumn("document_id")?.setFilterValue(event.target.value)
            }
            className="max-w-sm bg-surface border-white/10 text-text-primary placeholder:text-muted focus-visible:ring-blue-500/30"
          />
          
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
        </div>

        {/* Column Visibility */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="ml-auto bg-surface border-white/10 text-text-primary hover:bg-white/5">
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
                  <div className="text-muted">No documents found.</div>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <div className="flex-1 text-sm text-muted">
          {selectedCount > 0 && (
            <span>
              {selectedCount} of {table.getFilteredRowModel().rows.length} row(s) selected.
            </span>
          )}
        </div>
        <div className="flex items-center gap-6">
          <div className="text-sm text-muted">
            Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
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

      {/* Single Document Delete Confirmation */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent className="bg-surface border-white/10">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-text-primary flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-rose-400" />
              Delete Document?
            </AlertDialogTitle>
            <AlertDialogDescription className="text-secondary">
              {documentToDelete && (
                <div className="space-y-3 mt-4">
                  <p>You are about to permanently delete:</p>
                  <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                    <p className="font-mono text-sm text-text-primary mb-1">{documentToDelete.document_id}</p>
                    <p className="text-xs text-muted">
                      {documentToDelete.chunk_count} chunks • {documentToDelete.doc_type.toUpperCase()} • {documentToDelete.jurisdiction}
                    </p>
                  </div>
                  <p className="text-amber-400 text-sm">
                    <strong>Note:</strong> This will immediately rebuild the FAISS index.
                  </p>
                </div>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="bg-surface border-white/10 text-text-primary hover:bg-white/5">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={async () => {
                if (documentToDelete) {
                  await onDelete(documentToDelete.document_id)
                  setDocumentToDelete(null)
                }
              }}
              className="bg-rose-600 hover:bg-rose-500 text-white"
            >
              Delete Document
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Bulk Delete Confirmation */}
      <AlertDialog open={bulkDeleteDialogOpen} onOpenChange={setBulkDeleteDialogOpen}>
        <AlertDialogContent className="bg-surface border-white/10">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-text-primary flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-rose-400" />
              Delete {selectedCount} Document{selectedCount !== 1 ? 's' : ''}?
            </AlertDialogTitle>
            <AlertDialogDescription className="text-secondary">
              <div className="space-y-3 mt-4">
                <p>You are about to permanently delete {selectedCount} document{selectedCount !== 1 ? 's' : ''}. This action cannot be undone.</p>
                <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
                  <p className="text-amber-400 text-sm">
                    <strong>Warning:</strong> The FAISS index will be rebuilt immediately after deletion.
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
              onClick={async () => {
                const selectedRows = table.getFilteredSelectedRowModel().rows
                const count = selectedRows.length
                
                toast.promise(
                  async () => {
                    for (const row of selectedRows) {
                      await onDelete(row.original.document_id)
                    }
                    table.resetRowSelection()
                  },
                  {
                    loading: `Deleting ${count} document(s)...`,
                    success: `Successfully deleted ${count} document(s)`,
                    error: 'Failed to delete some documents',
                  }
                )
              }}
              className="bg-rose-600 hover:bg-rose-500 text-white"
            >
              Delete {selectedCount} Document{selectedCount !== 1 ? 's' : ''}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
