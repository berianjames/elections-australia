# Schema for Australian election data

This document is an overview of the database schema for the SQL database of historical Australian electoral data. The database provides information about Australian elections since federations through 2010, based on the information available in Adam Carr's psephos database (as such, it may be thought of as a re-presentation of those data).

## Main Tables
This section lists the tables and their functions. Schema for individual tables is given in the next section.

<table>
	<!--<tr><td><b></b></td><td></td></tr>-->
	<tr><td><b>elections</b></td><td>Election dates and types</td></tr>
	<tr><td><b>states</b></td><td>Australian states and territories</td></tr>
	<tr><td><b>electorates</b></td><td>Electorate names, populations and status in each election</td></tr>
	<tr><td><b>parties</b></td><td>Names and participation of electoral parties</td></tr>
	<tr><td><b>candidates</b></td><td>Names and electoral partipication of candidates</td></tr>
	<tr><td><b>counts_house</b></td><td>Raw (undistributed) vote counts for the House of Representatives at electorate level</td></tr>
	<tr><td><b>results_house</b></td><td>Final (distributed) vote counts for the House of Representatives at electorate level</td></tr>
	<tr><td><b>counts_senate_candidate</b></td><td>Raw (undistributed) vote counts for the Senate at candidate level</td></tr>
	<tr><td><b>results_senate</b></td><td>Final (distributed) vote counts for the Senate at state/territory level</td></tr>
	<tr><td><b>results_summary</b></td><td>Electoral result summary tables</td></tr>
 </table>

## Table Detail
This section gives the schema info for each of the database tables.

### elections

The <code>elections</code> table details each election since federation, with the following fields:
<table>
	<!--<tr><td></td><td></td></tr>-->
	<tr><td>id</td><td>primary key, election id</td></tr>
	<tr><td>level</td><td>type of election: federal or state</td></tr>
	<tr><td>chamber</td><td>chamber: House of Representative, Senate, Legislative Assembly or Legislative Council</td>
	<tr><td>date</td><td>date of election</td></tr>
	<tr><td>is_byelection</td><td>binary, is the election a by-election</td></tr>
</table>

### states

The Australian commonwealth is broken in six states and two territories. Federal senate elections are balloted up to state level, while House results are balloted at electorate level. 

<table>
	<!--<tr><td></td><td></td></tr>-->
	<tr><td>code</td><td>primary key, acronym for state/territory (UPPER CASE)</td></tr>
	<tr><td>state_name</td><td>common name of state/territory (First Upper Case)</td></tr>
	<!--<tr><td>created_at</td><td>date of federation</td></tr>-->
	<!--<tr><td>first_election_id</td><td>ID of first federal election in which state/territory</td></tr>-->
	<tr><td>is_territory</td><td>Binary flag dividing states and territories</td></tr>
</table>


### electorates

The <code>electorates</code> table details every electoral division involved in an election since federation. Electorates that persist between elections (even without redistribution) still hold distinct IDs in this table.
<table>
	<!--<tr><td></td><td></td></tr>-->
	<tr><td>id</td><td>primary key, electorate id</td></tr>
	<tr><td>election_id</td><td>election id</td></tr>
	<tr><td>electorate_name</td><td>elecorate name</td></tr>
	<tr><td>state_code</td><td>ID of electorate state/territory</td></tr>
	<tr><td>enrollments</td><td>electoral roll count at time of election</td></tr>
	<tr><td>ballots</td><td>ballots cast within electorate at election</td></tr>
	<!--<tr><td>informal</td><td>informal ballots cast within electorate at election</td></tr>-->
</table>


### parties

The <code>parties</code> table list all parties that have participated in state or federal elections.
<table>
	<!--<tr><td></td><td></td></tr>-->
	<tr><td>id</td><td>primary key, party id</td></tr>
	<tr><td>party_code</td><td>party short code</td></tr>
	<tr><td>party_name</td><td>party long name</td></tr>
	<tr><td>party_code_alt</td><td>alternate party short code</td></tr>
</table>


### candidates

The <code>candidates</code> lists every person every to run for office in an Australian state of federal election.
<table>
	<!--<tr><td></td><td></td></tr>-->
	<tr><td>id</td><td>primary key, candidate id</td></tr>
	<tr><td>election_id</td><td>election id</td></tr>
	<tr><td>name</td><td>candidate name</td></tr>
	<tr><td>party_id</td><td>ID of candidate's electoral party</td></tr>
</table>


### results_house

In the case that no candidate wins a majority in an electorate, the raw ballot counts in the House of Representatives are redistributed according to preferences indicated on the ballot, removing the candidate with the lowest ballot count at each step. When two candidates remain, the candidate with the majority is elected and the results for this are presented in <code>result_house</code>.
<table>
	<!--<tr><td></td><td></td></tr>-->
	<tr><td>id</td><td>primary key, count id</td></tr>
	<tr><td>election_id</td><td>election id</td></tr>
	<tr><td>electorate_id</td><td>electorate id</td></tr>
	<tr><td>candidate_id</td><td>candidate id</td></tr>
	<tr><td>votes_final</td><td>two-candidate redistributed final count</td></tr>
	<tr><td>is_elected</td><td>binary, is the candidate elected to parliament</td></tr>
</table>

### counts_house

The raw ballot counts for each candidate in every state and federal election for the House of Representatives are tabulated in <code>counts_house</code>.
<table>
	<!--<tr><td></td><td></td></tr>-->
	<tr><td>id</td><td>primary key, count id</td></tr>
	<tr><td>election_id</td><td>election id</td></tr>
	<tr><td>electorate_id</td><td>electorate id</td></tr>
	<tr><td>candidate_id</td><td>candidate id</td></tr>
	<tr><td>votes</td><td>number of votes cast for candidate</td></tr>
	<tr><td>is_incumbent</td><td>binary, is the candidate the incumbent</td></tr>
</table>


### counts_senate_candidate

The candidate-level results for every federal election for the Senate are tabulated in <code>counts_senate_candidate</code>.
<table>
	<!--<tr><td></td><td></td></tr>-->
	<tr><td>id</td><td>primary key, count id</td></tr>
	<tr><td>election_id</td><td>election id</td></tr>
	<tr><td>candidate_id</td><td>candidate id</td></tr>
	<tr><td>party_id</td><td>party id</td></tr>
	<tr><td>votes</td><td>number of votes cast for candidate</td></tr>
	<tr><td>is_elected</td><td>binary, is candidate elected under Hare-Clark system</td></tr>
</table>


### results_senate_state

The state- and territory-level results for every federal election for the Senate are tabulated in <code>counts_senate_state</code>.
<table>
	<!--<tr><td></td><td></td></tr>-->
	<tr><td>id</td><td>primary key, count id</td></tr>
	<tr><td>election_id</td><td>election id</td></tr>
	<tr><td>state</td><td>state/territory code</td></tr>
	<tr><td>party</td><td>name of party</td></tr>
	<tr><td>votes</td><td>number of ballots cast for party</td></tr>
	<tr><td>quotas</td><td>number of quotas received by party at initial count</td></tr>
	<tr><td>elected</td><td>number of senators elected from party after distribution</td></tr>
	<tr><td>incumbent</td><td>number of incumbent senators not due for election</td></tr>
	<tr><td>total</td><td>total number of senators for party after election</td></tr>
</table>

## Indices