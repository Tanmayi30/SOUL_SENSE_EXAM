'use client';

import React, { useState, useEffect } from 'react';
import { userApi } from '@/lib/api/user';
import { Loader2, ShieldAlert, History } from 'lucide-react';
import { Button } from '@/components/ui'; // Assuming Button exists based on login page

export default function SecurityPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    fetchLogs(1);
  }, []);

  const fetchLogs = async (pageNum: number) => {
    try {
      setLoading(true);
      setError('');
      const data = await userApi.getAuditLogs(pageNum, 20);

      if (pageNum === 1) {
        setLogs(data);
      } else {
        setLogs((prev) => [...prev, ...data]);
      }

      if (data.length < 20) {
        setHasMore(false);
      } else {
        setHasMore(true);
      }
      setPage(pageNum);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load logs');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadMore = () => {
    fetchLogs(page + 1);
  };

  return (
    <div className="min-h-screen bg-background p-6 lg:p-10">
      <div className="max-w-5xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center space-x-4 border-b pb-6">
          <div className="p-3 bg-primary/10 rounded-full">
            <ShieldAlert className="w-8 h-8 text-primary" />
          </div>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Security Activity</h1>
            <p className="text-muted-foreground mt-1">
              Review sensitive actions performed on your account.
            </p>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-destructive/10 text-destructive p-4 rounded-lg flex items-center gap-2">
            <ShieldAlert className="h-5 w-5" />
            <p>{error}</p>
          </div>
        )}

        {/* Logs Table */}
        <div className="bg-card rounded-xl border shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-muted/50 text-muted-foreground font-medium border-b">
                <tr>
                  <th className="px-6 py-4">Time (IST)</th>
                  <th className="px-6 py-4">Action</th>
                  <th className="px-6 py-4">Device</th>
                  <th className="px-6 py-4">IP Address</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {loading && page === 1 ? (
                  <tr>
                    <td colSpan={4} className="px-6 py-12 text-center">
                      <Loader2 className="h-6 w-6 animate-spin mx-auto text-muted-foreground" />
                      <p className="mt-2 text-muted-foreground">Loading activity...</p>
                    </td>
                  </tr>
                ) : logs.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-6 py-12 text-center text-muted-foreground">
                      <History className="h-10 w-10 mx-auto mb-3 opacity-20" />
                      No activity logs found.
                    </td>
                  </tr>
                ) : (
                  logs.map((log) => (
                    <tr key={log.id} className="hover:bg-muted/30 transition-colors">
                      <td className="px-6 py-4 font-mono text-xs">
                        {new Date(log.timestamp).toLocaleString('en-IN', {
                          timeZone: 'Asia/Kolkata',
                        })}
                      </td>
                      <td className="px-6 py-4 font-medium">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium 
                                            ${
                                              log.action.includes('LOGIN')
                                                ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                                                : log.action.includes('FAIL')
                                                  ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
                                                  : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
                                            }`}
                        >
                          {log.action}
                        </span>
                      </td>
                      <td className="px-6 py-4 max-w-[200px] truncate" title={log.user_agent}>
                        {log.user_agent ? log.user_agent.split(')')[0] + ')' : 'Unknown'}
                      </td>
                      <td className="px-6 py-4 font-mono text-xs text-muted-foreground">
                        {log.ip_address || 'Unknown'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Load More */}
          {logs.length > 0 && hasMore && (
            <div className="p-4 border-t text-center">
              <Button
                variant="ghost"
                onClick={handleLoadMore}
                disabled={loading}
                className="w-full sm:w-auto"
              >
                {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                Load Older Activity
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
