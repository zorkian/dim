# Distributed Infrastructure Monitoring (DIM)

## Description

This is super early, but think of it like a simple Nagios system
designed to work in infrastructures with tens of thousands of servers
(or more).

## Design

The basic premise of DIM is that in any suitably complicated
infrastructure you have a number of monitoring checks that you want to
be running at various intervals. These run the gamut of:

* Run xyz command on target system
* Run abc command on any system against target

Nagios allows you to do the former via the NRPE mechanism, and the
latter is done locally from the point of view of the Nagios instance.
This is fine, but when you start talking hundreds of thousands of
checks, the overhead becomes substantial and you need many instances.

DIM is designed to be a push based system. Individual machines are
responsible for pushing out their status updates (for local checks). The
remote checks are done slightly differently, in that the coordinators
are responsible for asking agents to run a remote check against someone
else, but the results are still pushed back upstream.

The DIM coordinators are nodes that use the Raft protocol to determine
a leader and keep everything orderly. The goal here is that, even in
the event of a failure of some number of coordinators, the system can
continue to monitor the infrastructure. A machine failure should not
require manual intervention.

## Topology Support

DIM is designed to be aware of topology. The short term design goal is
to try to allow situations where you have multiple data centers, and you
want to only do remote checks against other machines in the same data
center.

It is assumed for now that there is only one DIM coordinator set. We
will try to minimize bandwidth required between coordintaors and local
DIM agents -- persistent connections, using rollup queries (get status
of everything), pushing as much as possible to local checks, etc should
help with this.

## Machine Groups

This is designed for large infrastructures, where you will have
many types of machines. From the outset, DIM will need to support a
concept of grouping machines. The goal is to allow specifying possibly
overlapping groups, and the assumption is that nearly every check rule
will be written using groups.

## Checks

DIM checks are classified into either 'local' checks (the first class
that runs on a target machine being monitored) and 'remote' checks which
can run on any machine.

### Local Checks

A departure from the standard setup is that the DIM agent on any
particular machine will run the checks according to some schedule and
maintain a local state. This allows the DIM monitoring servers to
quickly fetch the results of potentially costly checks without having to
run them on-demand.

The DIM agent runs on each machine in the fleet and understands what
checks it should be running (possibly by downloading instructions from
the DIM coordinators, or possibly from reading local configuration
from disk and relying on admins to set up OOB transport of the
configurations).

Agents run checks according to the schedule and update some local state,
which should also be cached to disk so that agent restarts are quick and
pick up the last state.

Running local checks should be akin to writing cron jobs: you write
something that spits out an exit code + optional text, this is fired off
and captured by the DIM agent.

Additionally, local checks can run in "daemon" mode where they are
responsible for printing out lines of output. Each line is a JSON
formatted object that contains the results of that particular run. In
this mode, all we do is make sure the check runs, restart it if it
exits, and we capture its output into our local state.

### Local Daemon Checks

See the `local-checks/` directory for an example local daemon. They are
long-lived processes that output lines of JSON which the DIM agent then
makes available.

### Remote Checks

A remote check is a check that is run on a machine but targeted at
another machine in the fleet.

### Remote Daemon Checks

Much like a local daemon check, these are long-running processes. The
difference is that they're expected to read a command on STDIN (a
line-separated JSON structure) and then execute the check specified in
the command and return a result JSON object as a single line of output.

These checks will be used in a request-response cycle; you will read one
command, perform the requested check, and then write the result back to
STDOUT.

## Dependencies

We should support the concept of check dependencies: if X is firing,
then don't bother checking Y. The simplest implementation will be a tree
structure where you can specify which alerts depend on which others. We
should probably not allow cycles.

## Alerting/Output

The goal of DIM is, to be blunt, to know when things go wrong.

We should allow very simple specification of check states that, when
true, cause alerting logic to fire. The alerting logic can be fairly
straightforward for now, as we may want to build this out into a
separate system to handle logging, emailing vs. IM vs. paging, et
cetera.

We may even punt on the entire ability to specify alerting criteria
and just make DIM responsible for efficiently running millions of
checks, handling topologies and dependencies, and collecting the
results/publishing them to a log for someone else to import into a
timeseries system (which can then feed an alerting system).

## Licensing

See the LICENSE file for more information.

Written by Mark Smith <mark@qq.is>.
