/**
 * Conflict Resolution System
 * Resolves conflicts in collaborative editing
 */

export type ConflictType = 'edit' | 'delete' | 'move' | 'property';

export interface Conflict {
  id: string;
  type: ConflictType;
  timestamp: number;
  local: {
    userId: string;
    username: string;
    operation: any;
    version: number;
  };
  remote: {
    userId: string;
    username: string;
    operation: any;
    version: number;
  };
  resourceId: string;
  resourceType: string;
}

export type ResolutionStrategy = 'local' | 'remote' | 'merge' | 'manual';

export class ConflictResolver {
  private conflicts: Map<string, Conflict> = new Map();
  private autoResolveStrategies: Map<ConflictType, ResolutionStrategy> = new Map();

  constructor() {
    // Default auto-resolve strategies
    this.autoResolveStrategies.set('property', 'merge');
    this.autoResolveStrategies.set('move', 'remote'); // Last write wins
    this.autoResolveStrategies.set('edit', 'manual'); // Require manual resolution
    this.autoResolveStrategies.set('delete', 'manual');
  }

  detectConflict(
    resourceId: string,
    resourceType: string,
    localOp: any,
    remoteOp: any,
    localUser: { id: string; name: string },
    remoteUser: { id: string; name: string }
  ): Conflict | null {
    // Check if operations conflict
    if (!this.operationsConflict(localOp, remoteOp)) {
      return null;
    }

    const conflict: Conflict = {
      id: `conflict_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: this.determineConflictType(localOp, remoteOp),
      timestamp: Date.now(),
      local: {
        userId: localUser.id,
        username: localUser.name,
        operation: localOp,
        version: localOp.version || 0,
      },
      remote: {
        userId: remoteUser.id,
        username: remoteUser.name,
        operation: remoteOp,
        version: remoteOp.version || 0,
      },
      resourceId,
      resourceType,
    };

    this.conflicts.set(conflict.id, conflict);
    return conflict;
  }

  private operationsConflict(op1: any, op2: any): boolean {
    // Check if operations target the same property/field
    if (op1.path && op2.path) {
      return op1.path === op2.path && op1.timestamp !== op2.timestamp;
    }
    return false;
  }

  private determineConflictType(op1: any, op2: any): ConflictType {
    if (op1.type === 'delete' || op2.type === 'delete') {
      return 'delete';
    }
    if (op1.type === 'move' || op2.type === 'move') {
      return 'move';
    }
    if (op1.path === op2.path) {
      return 'property';
    }
    return 'edit';
  }

  autoResolve(conflictId: string): any | null {
    const conflict = this.conflicts.get(conflictId);
    if (!conflict) return null;

    const strategy = this.autoResolveStrategies.get(conflict.type);
    if (strategy === 'manual') {
      return null; // Requires manual resolution
    }

    return this.applyStrategy(conflict, strategy!);
  }

  private applyStrategy(conflict: Conflict, strategy: ResolutionStrategy): any {
    switch (strategy) {
      case 'local':
        return conflict.local.operation;
      
      case 'remote':
        return conflict.remote.operation;
      
      case 'merge':
        return this.mergeOperations(conflict.local.operation, conflict.remote.operation);
      
      default:
        return null;
    }
  }

  private mergeOperations(local: any, remote: any): any {
    // Three-way merge for compatible operations
    if (typeof local.value === 'object' && typeof remote.value === 'object') {
      return {
        ...local,
        value: { ...local.value, ...remote.value },
        merged: true,
      };
    }

    // Use newer timestamp
    return local.timestamp > remote.timestamp ? local : remote;
  }

  manualResolve(conflictId: string, resolution: ResolutionStrategy, customValue?: any): any {
    const conflict = this.conflicts.get(conflictId);
    if (!conflict) return null;

    let resolved;
    if (resolution === 'manual' && customValue !== undefined) {
      resolved = {
        ...conflict.local.operation,
        value: customValue,
        resolved: true,
      };
    } else {
      resolved = this.applyStrategy(conflict, resolution);
    }

    this.conflicts.delete(conflictId);
    return resolved;
  }

  getConflicts(): Conflict[] {
    return Array.from(this.conflicts.values());
  }

  getPendingCount(): number {
    return this.conflicts.size;
  }

  clear() {
    this.conflicts.clear();
  }
}

export const conflictResolver = new ConflictResolver();
