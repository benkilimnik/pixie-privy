/*
 * Copyright 2018- The Pixie Authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * SPDX-License-Identifier: Apache-2.0
 */

import * as React from 'react';

import { makeCancellable } from 'app/utils/cancellable-promise';

import { CommandProvider, CommandProviderResult } from './providers/command-provider';

/** Hook to passively update suggestions as the input and selection change in the command palette. */
export const useCommandProviders: (
  input: string, selection: [start: number, end: number],
) => CommandProviderResult[] = (
  input, selection,
) => {
  const providers: ReturnType<CommandProvider>[] = [
    // New providers will be added here in future commits.
    // Each one will have its own internal behavior, but ultimately resolve to a CommandProviderResult.
  ];

  const promises = React.useMemo(
    () => providers.map((provide) => provide(input, selection)),
    // Providers array doesn't change, its contents do.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [input, selection, ...providers],
  );

  const [out, setOut] = React.useState<CommandProviderResult[]>([]);

  React.useEffect(() => {
    const cancellable = makeCancellable(Promise.all(promises));
    cancellable.then((results) => {
      setOut(results.filter(({ completions }) => completions.length));
    });
    return () => cancellable.cancel();
  }, [promises]);

  return out;
};
